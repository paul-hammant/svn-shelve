import sh  # pip2 install sh
import shutil

sh.rm("-rf", "maven-gpg-plugin-WC")

sh.svn("co", "https://svn.apache.org/repos/asf/maven/plugins/trunk/maven-gpg-plugin/", "maven-gpg-plugin-WC")

shutil.make_archive("maven-gpg-plugin-WC", 'zip', "maven-gpg-plugin-WC")
