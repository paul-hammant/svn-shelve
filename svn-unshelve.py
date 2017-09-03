import sh  # pip2 install sh
import os
import tempfile
import shutil
import sys
import argparse

# TODO - cater for adds and deletes (and renames/moves)

def main(argv):

     parser = argparse.ArgumentParser(description='Svn Unshelve')

     parser.add_argument("stashname")
     parser.add_argument("working_copy")
     args = parser.parse_args(argv)

     orig_dir = os.getcwd()
     tmpdir = str(tempfile.mkdtemp())
     sh.cd(tmpdir)
     sh.git("clone", "-b", "master", orig_dir + "/" + args.stashname, _tty_out=False)
     sh.cd(orig_dir)

     sh.cd(tmpdir + "/" + args.stashname)
     svn_diff_names = sh.git("diff", "--name-only", "start..finish", _tty_out=False).splitlines()

     for file_name in svn_diff_names:
          sh.cp(tmpdir + "/" + args.stashname + "/" + file_name,
                orig_dir + "/" + args.working_copy + "/" + "/".join(file_name.split('/')[:-1]))

     sh.cd(orig_dir)
     shutil.rmtree(tmpdir)


if __name__ == "__main__":
    main(sys.argv)
