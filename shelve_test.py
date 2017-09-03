import fileinput
import os
import shutil
import tempfile
import zipfile

import sh

svn_shelve = __import__("svn-shelve")
svn_unshelve = __import__("svn-unshelve")


def test_that_basic_shelve_with_revert_works():

    delete_and_recreate_subversion_checkout()

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

    start_and_finish_are_the_only_two_git_commits(svn_log)


def test_that_shelve_with_add_and_revert_works():

    delete_and_recreate_subversion_checkout()

    change_a_file("maven-gpg-plugin-WC/pom.xml")
    write_to_file("hello/world.txt", "hello world", "maven-gpg-plugin-WC")
    sh.svn("add", "maven-gpg-plugin-WC/hello/")

    orig_changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert orig_changed == "A       hello\n" \
                           "A       hello/world.txt\n" \
                           "M       pom.xml\n"

    svn_shelve.main(["--revert_too", "foo.stash", "maven-gpg-plugin-WC"])

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed == "?       hello\n" # has that world.txt file too

    fileList, svn_log = contents_of_stash("/foo.stash")

    assert str(fileList) == "['./hello/world.txt', " \
                             "'./pom.xml', " \
                             "'./pom.xml.stash_info']"

    start_and_finish_are_the_only_two_git_commits(svn_log)

def test_that_shelve_with_add_and_without_revert_works():

    delete_and_recreate_subversion_checkout()

    change_a_file("maven-gpg-plugin-WC/pom.xml")
    write_to_file("hello/world.txt", "hello world", "maven-gpg-plugin-WC")
    sh.svn("add", "maven-gpg-plugin-WC/hello/")

    orig_changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert orig_changed == "A       hello\n" \
                           "A       hello/world.txt\n" \
                           "M       pom.xml\n"

    svn_shelve.main(["foo.stash", "maven-gpg-plugin-WC"])

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed == orig_changed

    fileList, svn_log = contents_of_stash("/foo.stash")

    assert str(fileList) == "['./hello/world.txt', " \
                             "'./pom.xml', " \
                             "'./pom.xml.stash_info']"

    start_and_finish_are_the_only_two_git_commits(svn_log)


def start_and_finish_are_the_only_two_git_commits(svn_log):
    assert len(svn_log) == 2
    assert svn_log[0].endswith(" finish")
    assert svn_log[1].endswith(" start")


def test_that_shelve_without_reset_works():

    delete_and_recreate_subversion_checkout()

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

    start_and_finish_are_the_only_two_git_commits(svn_log)


def test_that_basic_unshelve_works():

    delete_and_recreate_subversion_checkout()

    change_a_file("maven-gpg-plugin-WC/pom.xml")
    change_a_file("maven-gpg-plugin-WC/src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java")
    svn_shelve.main(["foo.stash", "maven-gpg-plugin-WC"])

    sh.rm("-rf", "maven-gpg-plugin-WC")
    create_subversion_checkout()

    orig_changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert orig_changed == ""

    svn_unshelve.main(["foo.stash", "maven-gpg-plugin-WC"])

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed == "M       pom.xml\n" \
                      "M       src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java\n"

def delete_and_recreate_subversion_checkout():
    delete_temp_files()
    create_subversion_checkout()


def create_subversion_checkout():
    zipfile.ZipFile("maven-gpg-plugin-WC.zip").extractall("maven-gpg-plugin-WC")


def delete_temp_files():

    sh.rm("-rf", "maven-gpg-plugin-WC")
    sh.rm("-rf", "foo.stash")


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


def write_to_file(file_name, contents, indir):
    sh.mkdir("-p", indir + "/" + "/".join(file_name.split('/')[:-1]))
    f = open(indir + "/" + file_name, 'w')
    f.writelines(contents)
    f.close()


def change_a_file(file):
    # Change two files.
    for line in fileinput.input(file, inplace=True):
        print "%d: %s" % (fileinput.filelineno(), line),

