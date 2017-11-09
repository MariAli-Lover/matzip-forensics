DEFAULT_SECTORS_PER_CLUSTER = 8

class VFS:
    def __init__(self, drive, spc = DEFAULT_SECTORS_PER_CLUSTER):
        self.drive = drive
        self.spc = spc

    def seek(self, offset):
        self.drive.seek(self.spc * offset)

    def read(self, clusters):
        return self.drive.read(self.spc * clusters)
