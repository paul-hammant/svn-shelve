import fileinput
import os
import glob2
import shutil
import tempfile
import zipfile

import sh

svn_shelve = __import__("svn-shelve")


def test_that_shelve_with_reset_works():

    delete_temp_files()

    zipfile.ZipFile("maven-gpg-plugin-WC.zip").extractall("maven-gpg-plugin-WC")

    change_a_file("maven-gpg-plugin-WC/pom.xml")
    change_a_file("maven-gpg-plugin-WC/src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java")

    orig_changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert orig_changed == "M       pom.xml\n" \
                           "M       src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java\n"

    svn_shelve.main(["--revert_too", "foo.stash", "maven-gpg-plugin-WC"])

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed == ""  # no pending changes anymore


    fileList, svn_log = contents_of_stash("/foo.stash")

    assert str(fileList) == "['./pom.xml', " \
                             "'./pom.xml.stash_info', " \
                             "'./src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java', " \
                             "'./src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java.stash_info']"
    assert len(svn_log) == 2
    assert svn_log[0].endswith(" finish")
    assert svn_log[1].endswith(" start")


def delete_temp_files():

    sh.rm("-rf", "maven-gpg-plugin-WC")
    sh.rm("-rf", "foo.stash")


def test_that_shelve_without_reset_works():

    delete_temp_files()

    zipfile.ZipFile("maven-gpg-plugin-WC.zip").extractall("maven-gpg-plugin-WC")

    change_a_file("maven-gpg-plugin-WC/pom.xml")
    change_a_file("maven-gpg-plugin-WC/src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java")

    orig_changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert orig_changed == "M       pom.xml\n" \
                           "M       src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java\n"

    svn_shelve.main(["foo.stash", "maven-gpg-plugin-WC"])

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed == orig_changed  # changes are still there

    fileList, svn_log = contents_of_stash("/foo.stash")

    assert str(fileList) == "['./pom.xml', " \
                             "'./pom.xml.stash_info', " \
                             "'./src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java', " \
                             "'./src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java.stash_info']"

    assert len(svn_log) == 2
    assert svn_log[0].endswith(" finish")
    assert svn_log[1].endswith(" start")


def contents_of_stash(stashfile):
    orig_dir = os.getcwd()
    tmpdir = clone_from_stash_bundle(orig_dir, stashfile)
    sh.cd(tmpdir + stashfile)
    svn_log = sh.git("log", "--pretty=oneline", "--no-color", _tty_out=False).splitlines()
    fileList = sorted_list_of_files()
    sh.cd(orig_dir)
    shutil.rmtree(tmpdir)
    return fileList, svn_log


def clone_from_stash_bundle(orig_dir, stashfile):
    tmpdir = str(tempfile.mkdtemp())
    sh.cd(tmpdir)
    sh.git("clone", "-b", "master", orig_dir + stashfile, _tty_out=False)
    sh.cd(orig_dir)
    return tmpdir


def sorted_list_of_files():
    fileList = []
    for root, subFolders, files in os.walk("."):
        for file in files:
            if not root.startswith("./.git"):
                fileList.append(os.path.join(root, file))
    fileList.sort()
    return fileList


def change_a_file(file):
    # Change two files.
    for line in fileinput.input(file, inplace=True):
        print "%d: %s" % (fileinput.filelineno(), line),

