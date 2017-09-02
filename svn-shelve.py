import sh  # pip2 install sh
import os
from stat import S_IWUSR, S_IREAD
import tempfile
import shutil


# TODO - split tests into tests.py (etc).
# TODO - parameterize, make into utility
# TODO - cater for adds and deletes (and renames/moves)
# TODO - named shelves
# TODO - unshelve too
import sys

def main(command, stashname, working_copy):

     tmpdir = str(tempfile.mkdtemp())

     print tmpdir

     # While files changed?
     files = sh.svn("st", working_copy)

     sh.git("init", tmpdir)

     # Copy originals in.
     splitlines = files.splitlines()
     for line in splitlines:
          file_name = line[1:].strip()
          info = sh.svn("info", file_name)
          for iLine in info:
               if iLine.startswith("Checksum:"):
                    checksum = iLine.split(" ")[1].strip()
                    dir = checksum[0:2]
                    sh.mkdir("-p", tmpdir + "/" + "/".join(file_name.split('/')[:-1]))
                    sh.cp(working_copy + "/.svn/pristine/" + dir + "/" + checksum + ".svn-base", tmpdir + "/" + file_name)
                    os.chmod(tmpdir + "/" + file_name, S_IWUSR | S_IREAD)  # make writable
          f = open(tmpdir + "/" + file_name + ".info", 'w')
          f.writelines(info)
          f.close()

     # Do a commit
     orig_dir = os.getcwd()
     sh.cd(tmpdir)
     sh.git("add", ".")
     sh.git("commit", "-m", "start")
     sh.git("tag", "-a", "start", "-m", "start")
     sh.cd(orig_dir)

     # Copy changed versions in.
     for line in splitlines:
          file_name = line[1:].strip()
          sh.cp(file_name, tmpdir + "/" + file_name)

     # Do a commit
     sh.cd(tmpdir)
     sh.git("add", ".")
     sh.git("commit", "-m", "finish")
     sh.git("tag", "-a", "finish", "-m", "finish")


     sh.git("bundle", "create", orig_dir + "/" + stashname, "master")

     sh.cd(orig_dir)

     shutil.rmtree(tmpdir)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[2])