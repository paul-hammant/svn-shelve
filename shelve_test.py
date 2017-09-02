import fileinput
import zipfile

import ansiconv
import sh

svn_shelve = __import__("svn-shelve")


def test_answer():

    sh.rm("-rf", "maven-gpg-plugin-WC")

    zipfile.ZipFile("maven-gpg-plugin-WC.zip").extractall("maven-gpg-plugin-WC")

    # Change two files.
    for line in fileinput.input("maven-gpg-plugin-WC/pom.xml", inplace=True):
        print "%d: %s" % (fileinput.filelineno(), line),
    for line in fileinput.input("maven-gpg-plugin-WC/src/main/java/org/apache/maven/plugin/gpg/SigningBundle.java",
                                inplace=True):
        print "%d: %s" % (fileinput.filelineno(), line),

    svn_shelve.main([])

    sh.cd("shelve")
    log = sh.git("log", "--pretty=oneline", "--no-color", _tty_out=False).splitlines()

    assert len(log) == 2
    assert log[0].endswith(" finish")
    assert log[1].endswith(" start")

