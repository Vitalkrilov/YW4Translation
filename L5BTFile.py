# Level5 Binary Text parser

import sys
import struct
import os
import json
import myutils



# We could use floats but let it be like now...
def getEntryLength(entryLength):
  result = 3
  if entryLength <= 12:
    return result
  multiplier = (entryLength - 13) // 16 + 1
  return result + multiplier * 4

class BinaryReader:
  def __init__(self, filename):
    self.f = open(filename, 'rb')
    self.f_size = os.path.getsize(filename)

  def close(self):
    self.f.close()

  def getSize(self):
    return self.f_size

  def seek(self, pos):
    self.f.seek(pos)

  def tell(self):
    return self.f.tell()

  def readByte(self):
    return ord(self.f.read(1))

  def readBytes(self, count):
    return self.f.read(count)

  def readStringBytes(self):
    res = b''
    while True:
      currentByte = self.f.read(1)
      if currentByte == b'\x00':
        break
      res += currentByte
    return res

  def __unpack(self, format, size):
    data = self.f.read(size)
    return struct.unpack(format, data)

  def readInt32(self):
    return self.__unpack('i', 4)[0]

  def readUInt32(self):
    return self.__unpack('I', 4)[0]

class BinaryWriter:
  def __init__(self, filename):
    self.f = open(filename, 'wb')

  def close(self):
    self.f.close()

  # data: int in range [0; 255]
  def writeByte(self, data):
    self.f.write(data.to_bytes(1, sys.byteorder))

  def writeBytes(self, data):
    self.f.write(data)

  def writeInt32(self, data):
    self.f.write(struct.pack('i', data))

  def writeUInt32(self, data):
    self.f.write(struct.pack('I', data))

  def writeAlignment(self, alignment, alignmentByte):
    remainder = self.f.tell() % alignment
    if remainder <= 0:
      return
    for i in range(alignment - remainder):
      self.writeByte(alignmentByte)

class Header:
  def __init__(self):
    self.entryCount = 0
    self.stringSecOffset = 0
    self.stringSecSize = 0
    self.stringCount = 0

  def deserialize(self, data):
    data = struct.unpack('iiii', data)
    self.entryCount = data[0]
    self.stringSecOffset = data[1]
    self.stringSecSize = data[2]
    self.stringCount = data[3]

  def serialize(self):
    return struct.pack('iiii', self.entryCount, self.stringSecOffset, self.stringSecSize, self.stringCount)

class Entry:
  def __init__(self, entryTypeID, typeMask):
    self.entryTypeID = entryTypeID
    self.typeMask = typeMask
    self.data = []

class DataEntry:
  def __init__(self, bType, value):
    self.bType = bType # 2-bit value: 0 - string offset, 1 - integer, 2 - float[, 3 - nothing]
    self.value = value

class Label:
  def __init__(self, relOffset, text):
    self.relOffset = relOffset
    self.text = text
    self.connections = []

class L5BTFile:
  def __init__(self, filename):
    self.filename = filename
    self.reinitialize() # needed for adding some fields

  def reinitialize(self):
    self.loaded = False
    self.corrupted = False

    self.entries = []
    self.labels = []
    self.header = Header()
    self.encoding = ''
    self.sig = b''

  def load(self):
    self.reinitialize()

    br = BinaryReader(self.filename)

    # Get file encoding
    br.seek(br.getSize() - 0xa)
    self.encoding = br.readByte()
    if self.encoding == 0:
      self.encoding = 'sjis'
    elif self.encoding == 1:
      self.encoding = 'utf8'
    else:
      if not self.corrupted:
        self.corrupted = True
        myutils.eprint(f'{sys.argv[0]}: warning: file corrupted (unknown encoding type (value: {hex(self.encoding)})) ["{self.filename}"]')
    br.seek(0)

    # Read header
    self.header.deserialize(br.readBytes(4*4))

    # Get entries
    for i in range(self.header.entryCount):
      entryTypeID = br.readUInt32()
      entryLength = br.readByte()
      entry = Entry(entryTypeID, br.readBytes(getEntryLength(entryLength)))

      mask = list(reversed(entry.typeMask))
      for j in range(len(mask)):
        for skipCount in range(0, 8, 2):
          bType = (mask[j] & (0b11 << skipCount)) >> skipCount; # choosing 2 bits (smth like 0b00[11]0000)
          if bType != 0b11:
            entry.data.append(DataEntry(bType, br.readUInt32()))
          if len(entry.data) == entryLength:
            break
        if len(entry.data) == entryLength:
          break
      if len(entry.data) != entryLength:
        if not self.corrupted:
          self.corrupted = True
          myutils.eprint(f'{sys.argv[0]}: warning: file corrupted (expected {entryLength} entries but got {len(entry.data)}) ["{self.filename}"]')
      self.entries.append(entry)

    # Get labels
    for entryIdx in range(len(self.entries)):
      for dataIdx in range(len(self.entries[entryIdx].data)):
        d = self.entries[entryIdx].data[dataIdx]

        if d.bType == 0 and d.value != 0xffffffff:
          if d.value >= self.header.stringSecSize:
            if not self.corrupted:
              self.corrupted = True
              myutils.eprint(f'{sys.argv[0]}: warning: file corrupted (got string offset outside strings block) ["{self.filename}"]')
          else:
            index = -1
            for i in range(len(self.labels)):
              # NOTICE: it's all cool -- having many entries link to one string -- but there is no code for handling different offsets for one string (it's possible but almost nobody needs this). I don't want to write unneeded code but still keep this in mind.
              if self.labels[i].relOffset == d.value:
                index = i

            if index == -1:
              br.seek(self.header.stringSecOffset + d.value)
              self.labels.append(Label(d.value, br.readStringBytes().decode(self.encoding).replace('\\n', '\n')))
              self.labels[-1].connections.append((dataIdx, entryIdx))
            else:
              self.labels[index].connections.append((dataIdx, entryIdx))

    # Signature
    br.seek((br.tell() + 0xf) & ~0xf)
    self.sig = br.readBytes(br.getSize() - br.tell())

    br.close()

    if self.rebuildStringOffsets():
      if not self.corrupted:
        self.corrupted = True
        myutils.eprint(f'{sys.argv[0]}: warning: file corrupted (strings were not packed in right way) ["{l5tb_file.filename}"]')

    self.loaded = True

  # forcely: use it if you need to rebuild all connections (entries <-> labels)
  def rebuildStringOffsets(self, forcely=False):
    changed = False

    relOffset = 0
    # NOTICE: Strings could be in other order (developers used this order, obviously). If so then it will be treated as corrupted
    for label in self.labels:
      if label.relOffset != relOffset or forcely:
        if label.relOffset != relOffset:
          changed = True
        for point in label.connections:
          self.entries[point[1]].data[point[0]].value = relOffset
        label.relOffset = relOffset

      byteCount = len(label.text.replace('\n', '\\n').replace('\x0a', '\\n').encode(self.encoding)) + 1
      relOffset += byteCount
    if self.header.stringSecSize != relOffset:
      changed = True
    self.header.stringSecSize = relOffset

    return changed

  def save(self):
    self.rebuildStringOffsets()

    bw = BinaryWriter(self.filename)

    # Header
    bw.writeBytes(self.header.serialize())

    # Entries
    for entry in self.entries:
      bw.writeUInt32(entry.entryTypeID)
      bw.writeByte(len(entry.data))
      bw.writeBytes(entry.typeMask)
      for data in entry.data:
        bw.writeUInt32(data.value)
    bw.writeAlignment(0x10, 0xff)

    # Text
    for label in self.labels:
      bw.writeBytes(label.text.replace('\n', '\\n').replace('\x0a', '\\n').encode(self.encoding))
      bw.writeByte(0x00)
    bw.writeAlignment(0x10, 0xff)

    bw.writeBytes(self.sig)

    bw.close()

  def fromJSON(self, jsonStr):
    self.reinitialize()

    data = json.loads(jsonStr)
    self.sig = bytes(data['signature'])
    self.encoding = self.sig[-0xa]
    if self.encoding == 0:
      self.encoding = 'sjis'
    elif self.encoding == 1:
      self.encoding = 'utf8'
    else:
      if not self.corrupted:
        self.corrupted = True
        myutils.eprint(f'{sys.argv[0]}: warning: file corrupted (unknown encoding type (value: {hex(self.encoding)})) ["{self.filename}"]')
    self.header.stringCount = len(data['strings'])
    self.header.entryCount = len(data['entries'])
    # some consts
    HEADERSIZE = 4*4
    IDANDLEN = 4 + 1
    self.header.stringSecOffset = HEADERSIZE + len(data['entries']) * IDANDLEN

    for e in data['strings']:
      self.labels.append(Label(0, e))

    for e in data['entries']:
      typeMaskLength = getEntryLength(len(e['data']))
      b2Count = typeMaskLength*4 - len(e['data']) # count of 2 bits
      ffCount = b2Count // 4 # count of full bytes
      entry = Entry(e['id'], b'\x00' * (typeMaskLength - ffCount) + b'\xff' * ffCount)
      self.header.stringSecOffset += len(entry.typeMask) + len(e['data']) * 4
      entry.typeMask = list(entry.typeMask)

      for i in range(len(e['data'])):
        el = e['data'][i]
        if type(el) == int:
          bType = 1
          val = el
        else:
          bType = el['type']
          if bType == -1:
            bType = 0
            val = 0
            self.labels[el['value']].connections.append((i, len(self.entries)))
          else:
            val = el['value']
        el = DataEntry(bType, val)
        entry.data.append(el)

        current2Bit = ffCount * 4 + i
        entry.typeMask[-(current2Bit // 4 + 1)] |= (bType << ((current2Bit % 4)*2))

      entry.typeMask = bytes(entry.typeMask)
      self.entries.append(entry)

    # Adding offset
    mod16 = self.header.stringSecOffset % 16
    if mod16 != 0:
      self.header.stringSecOffset += 16 - mod16

    self.rebuildStringOffsets(True)

    self.loaded = True

  def toJSON(self):
    data = dict()
    data['signature'] = list(self.sig)
    data['entries'] = []

    data['strings'] = []
    relOffset2idx = dict()
    currentIdx = 0
    for e in self.labels:
      data['strings'].append(e.text)
      relOffset2idx[e.relOffset] = currentIdx
      currentIdx += 1

    for e in self.entries:
      entry = dict()
      entry['id'] = e.entryTypeID
      entry['data'] = []
      for e1 in e.data:
        if e1.bType == 0 and e1.value != 0xffffffff and e1.value < self.header.stringSecSize: # last checking is just for more compatibility (but not guarantee right work at all)
          entry['data'].append({'type': -1, 'value': relOffset2idx[e1.value]})
        elif e1.bType == 1:
          entry['data'].append(e1.value)
        else:
          entry['data'].append({'type': e1.bType, 'value': e1.value})
      data['entries'].append(entry)

    return json.dumps(data, indent=2, ensure_ascii=False)

  def __str__(self):
    res = ''

    res +=  'L5BT File\n'
    res += f'filename: {self.filename}\n'
    res += f'loaded: {self.loaded}\n'
    res += f'encoding: {self.encoding}\n'
    res += f'sig: {self.sig}\n'
    res +=  'header:\n'
    res += f' entryCount: {self.header.entryCount}\n'
    res += f' stringSecOffset: {self.header.stringSecOffset}\n'
    res += f' stringSecSize: {self.header.stringSecSize}\n'
    res += f' stringCount: {self.header.stringCount}\n'
    res +=  'entries:\n'
    for entry in self.entries:
      res += f' - entryTypeID: {entry.entryTypeID}\n'
      res += f'   typeMask: {entry.typeMask}\n'
      res +=  '   data:\n'
      for dentry in entry.data:
        if dentry.bType == 0:
          typeOfType = 'string offset'
        elif dentry.bType == 1:
          typeOfType = 'integer'
        elif dentry.bType == 2:
          typeOfType = 'float'
        else:
          typeOfType = 'unknown'
        res += f'    - bType: {dentry.bType} (type: {typeOfType})\n'
        res += f'      value: {dentry.value} (hex: {hex(dentry.value)})\n'
        if dentry.bType == 0 and dentry.value != 0xffffffff and dentry.value < self.header.stringSecSize:
          found = False
          for e in self.labels:
            if e.relOffset == dentry.value:
              res += '      string: "' + e.text.replace('\n', '\\n') + '"\n'
              found = True
              break
          if not found:
            res += '      string: [Not found!]\n'
    res +=  'labels:\n'
    for l in self.labels:
      res += f' - relOffset: {l.relOffset}\n'
      res +=  '   text: "' + l.text.replace('\n', '\\n') + '"\n'
      res +=  '   text bytes (with null term.): "' + str(len(l.text.replace('\n', '\\n').encode(self.encoding))) + '"\n'
      res +=  '   connections:\n'
      for p in l.connections:
        res += f'    - x: {p[0]}, y: {p[1]}\n'

    return res
