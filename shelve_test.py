import fileinput
import os
import glob2
import shutil
import tempfile
import zipfile

import sh

svn_shelve = __import__("svn-shelve")


def test_that_shelve_with_reset_works():

    sh.rm("-rf", "maven-gpg-plugin-WC")
    sh.rm("-rf", "foo.stash")

    zipfile.ZipFile("maven-gpg-plugin-WC.zip").extractall("maven-gpg-plugin-WC")

    change_a_file("maven-gpg-plugin-WC/pom.xml")
    change_a_file("maven-gpg-plugin-WC/src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java")

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed != ""  # some changes

    svn_shelve.main(["--revert_too", "foo.stash", "maven-gpg-plugin-WC"])

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed == ""  # no changes


    tmpdir = str(tempfile.mkdtemp())

    orig_dir = os.getcwd()

    sh.cd(tmpdir)
    sh.git("clone", "-b", "master",  orig_dir + "/foo.stash", _tty_out=False)

    sh.cd(tmpdir + "/foo.stash")
    log = sh.git("log", "--pretty=oneline", "--no-color", _tty_out=False).splitlines()

    files = str(glob2.glob("**/*"))

    shutil.rmtree(tmpdir)

    sh.cd(orig_dir)

    assert files == "['pom.xml', 'pom.xml.info', 'src', " \
                    "'src/main', 'src/main/java', 'src/main/java/org', " \
                    "'src/main/java/org/apache', 'src/main/java/org/apache/maven', " \
                    "'src/main/java/org/apache/maven/plugin', " \
                    "'src/main/java/org/apache/maven/plugin/gpg', " \
                    "'src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java', " \
                    "'src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java.info']"

    assert len(log) == 2
    assert log[0].endswith(" finish")
    assert log[1].endswith(" start")

    # sh.cd(tmpdir + "maven-gpg-plugin-WC")

    # changed = sh.svn("st")


def test_that_shelve_without_reset_works():

    sh.rm("-rf", "maven-gpg-plugin-WC")
    sh.rm("-rf", "foo.stash")

    zipfile.ZipFile("maven-gpg-plugin-WC.zip").extractall("maven-gpg-plugin-WC")

    change_a_file("maven-gpg-plugin-WC/pom.xml")
    change_a_file("maven-gpg-plugin-WC/src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java")

    orig_changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert orig_changed != ""  # some changes

    svn_shelve.main(["foo.stash", "maven-gpg-plugin-WC"])

    changed = sh.svn("st", "maven-gpg-plugin-WC").replace("maven-gpg-plugin-WC/", "")
    assert changed == orig_changed  # changes are still there

    tmpdir = str(tempfile.mkdtemp())

    orig_dir = os.getcwd()

    sh.cd(tmpdir)
    sh.git("clone", "-b", "master",  orig_dir + "/foo.stash", _tty_out=False)

    sh.cd(tmpdir + "/foo.stash")
    log = sh.git("log", "--pretty=oneline", "--no-color", _tty_out=False).splitlines()

    files = str(glob2.glob("**/*"))

    shutil.rmtree(tmpdir)

    sh.cd(orig_dir)

    assert files == "['pom.xml', 'pom.xml.info', 'src', " \
                    "'src/main', 'src/main/java', 'src/main/java/org', " \
                    "'src/main/java/org/apache', 'src/main/java/org/apache/maven', " \
                    "'src/main/java/org/apache/maven/plugin', " \
                    "'src/main/java/org/apache/maven/plugin/gpg', " \
                    "'src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java', " \
                    "'src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java.info']"

    assert len(log) == 2
    assert log[0].endswith(" finish")
    assert log[1].endswith(" start")

    # sh.cd(tmpdir + "maven-gpg-plugin-WC")

    # changed = sh.svn("st")



def change_a_file(file):
    # Change two files.
    for line in fileinput.input(file, inplace=True):
        print "%d: %s" % (fileinput.filelineno(), line),

