import sh  # pip2 install sh
import os
from stat import S_IWUSR, S_IREAD

import fileinput

# TODO - split tests into tests.py (etc).
# TODO - parameterize, make into utility
# TODO - cater for adds and deletes (and renames/moves)
# TODO - named shelves
# TODO - unshelve too

sh.rm("-rf", "maven-gpg-plugin")
sh.rm("-rf", "shelve")

sh.svn("co", "https://svn.apache.org/repos/asf/maven/plugins/trunk/maven-gpg-plugin/")

# Change two files.
for line in fileinput.input("maven-gpg-plugin/pom.xml", inplace=True):
     print "%d: %s" % (fileinput.filelineno(), line),
for line in fileinput.input("maven-gpg-plugin/src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java", inplace=True):
     print "%d: %s" % (fileinput.filelineno(), line),

# While files changed?
files = sh.svn("st", "maven-gpg-plugin")

sh.mkdir("shelve")
sh.git("init", "shelve")

# Copy originals in.
for line in files.splitlines():
     file_name = line[1:].strip()
     info = sh.svn("info", file_name)
     for iLine in info:
          if iLine.startswith("Checksum:"):
               checksum = iLine.split(" ")[1].strip()
               dir = checksum[0:2]
               sh.mkdir("-p", "shelve/" + "/".join(file_name.split('/')[:-1]))
               sh.cp("maven-gpg-plugin/.svn/pristine/" + dir + "/" + checksum + ".svn-base", "shelve/" + file_name)
               os.chmod("shelve/" + file_name, S_IWUSR | S_IREAD) # make writable
     f = open("shelve/" + file_name + ".info", 'w')
     f.writelines(info)
     f.close()

# Do a commit
sh.cd("shelve")
sh.git("add", ".")
sh.git("commit", "-m", "start")
sh.cd("..")

# Copy changed versions in.
for line in files.splitlines():
     file_name = line[1:].strip()
     sh.cp(file_name, "shelve/" + file_name)

# Do a commit
sh.cd("shelve")
sh.git("add", ".")
sh.git("commit", "-m", "finish")
sh.cd("..")