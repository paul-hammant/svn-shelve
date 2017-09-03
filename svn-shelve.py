import sh  # pip2 install sh
import os
from stat import S_IWUSR, S_IREAD
import tempfile
import shutil
import sys
import argparse


# TODO - split tests into tests.py (etc).
# TODO - parameterize, make into utility
# TODO - cater for adds and deletes (and renames/moves)
# TODO - named shelves
# TODO - unshelve too

def main(argv):

     parser = argparse.ArgumentParser(description='Svn Shelve')

     parser.add_argument("stashname")
     parser.add_argument("working_copy")
     parser.add_argument("--revert_too", help="Revet working copy pending changes too",
                         action="store_true")

     args = parser.parse_args(argv)

     tmpdir = str(tempfile.mkdtemp())

     print tmpdir

     # While files changed?
     files = sh.svn("st", args.working_copy).replace(args.working_copy + "/", "")

     sh.git("init", tmpdir)

     # Copy originals in.
     splitlines = files.splitlines()
     for line in splitlines:
          file_name = line[1:].strip()
          info = sh.svn("info", args.working_copy + "/" + file_name)
          for iLine in info:
               if iLine.startswith("Checksum:"):
                    checksum = iLine.split(" ")[1].strip()
                    dir = checksum[0:2]
                    sh.mkdir("-p", tmpdir + "/" + "/".join(file_name.split('/')[:-1]))
                    sh.cp(args.working_copy + "/.svn/pristine/" + dir + "/" + checksum + ".svn-base", tmpdir + "/" + file_name)
                    os.chmod(tmpdir + "/" + file_name, S_IWUSR | S_IREAD)  # make writable
          f = open(tmpdir + "/" + file_name + ".stash_info", 'w')
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
          sh.cp(args.working_copy + "/" + file_name, tmpdir + "/" + file_name)

     # Do a commit
     sh.cd(tmpdir)
     sh.git("add", ".")
     sh.git("commit", "-m", "finish")
     sh.git("tag", "-a", "finish", "-m", "finish")

     sh.git("bundle", "create", orig_dir + "/" + args.stashname, "master")

     sh.cd(orig_dir)

     shutil.rmtree(tmpdir)

     if args.revert_too:
          for line in splitlines:
               file_name = line[1:].strip()
               sh.svn("revert", args.working_copy + "/" + file_name)

if __name__ == "__main__":
    main(sys.argv)
