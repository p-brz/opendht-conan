from conans import ConanFile, CMake, tools
import os
from os import path

class OpendhtConan(ConanFile):
    name = "opendht"
    version = "1.2.1"
    license = "GPLv3"
    url = "https://github.com/paulobrizolara/opendht-conan"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports = ("CMakeLists.txt",)

    options = {"shared": [True, False], "build_tools" : [True, False]}
    default_options = "shared=True", "build_tools=False", "msgpack-c:header_only=False"

    requires = (
        "gnutls/3.4.16@DEGoodmanWilson/testing",
        "nettle/3.3@DEGoodmanWilson/testing",
        "msgpack-c/1.4.2@paulobrizolara/stable"
    )

    REPO = "https://github.com/savoirfairelinux/opendht/"
    ZIP_URL = "%s/archive/%s.tar.gz" % (REPO, version)
    #Folder inside the zip
    ZIP_FOLDER_NAME = "opendht-" + version
    UNZIPPED_DIR = "opendht"
    FILE_SHA = '138c43fea4b032eb8a9e78fb0576001ea43741344b17e2f4830b691c0e6850d4'

    def source(self):
        zip_name = "%s.tar.gz" % self.name

        tools.download(self.ZIP_URL, zip_name)
        tools.check_sha256(zip_name, self.FILE_SHA)
        tools.untargz(zip_name)
        os.unlink(zip_name)

        os.rename(self.ZIP_FOLDER_NAME, self.UNZIPPED_DIR)

    def build(self):
        #Make build dir
        build_dir = self.try_make_dir(os.path.join(".", "build"))

        #Change to build dir
        os.chdir(build_dir)
        src_dir = self.conanfile_directory

        cmake = CMake(self.settings)
        cmake_args = self.cmake_args()

        self.output.info('cmake "%s" %s %s' % (src_dir, cmake.command_line, cmake_args))

        self.run('cmake "%s" %s %s' % (src_dir, cmake.command_line, cmake_args))
        self.run('cmake --build . --target install %s' % cmake.build_config)

    def package(self):
        self.copy("**.h", src=path.join(self.UNZIPPED_DIR, "include"), dst="include", keep_path=True)
#        self.copy("*", src=path.join("build", "lib"), dst="lib")

    def package_info(self):
        self.cpp_info.libs      = ["opendht"]
        self.cpp_info.cppflags  = ["-std=%s" % self.get_std_value()]

        self.cpp_info.includedirs += self.deps_cpp_info["msgpack-c"].include_paths
        self.cpp_info.includedirs += self.deps_cpp_info["gnutls"].include_paths

        for lib in ("gnutls", "nettle", "libiconv", "gmp", "gnutls", "zlib"):
            self.cpp_info.libdirs     += self.deps_cpp_info[lib].lib_paths
            self.cpp_info.libs        += self.deps_cpp_info[lib].libs


####################################### Helpers ################################################

    def cmake_args(self):
        """Generate arguments for cmake"""

        if not hasattr(self, 'package_folder'):
            self.package_folder = "dist"

        args = [
                self.cmake_bool_option("OPENDHT_SHARED", self.options.shared),
                self.cmake_bool_option("OPENDHT_TOOLS"    , self.options.build_tools)
        ]
        args += ['-DCMAKE_INSTALL_PREFIX="%s"' % self.package_folder]

        return ' '.join(args)

    def cmake_bool_option(self, name, value):
        return "-D%s=%s" % (name.upper(), "ON" if value else "OFF");

    def get_std_value(self):
        std_value = getattr(self.scope, 'std', None)
        if not std_value:
            std_value = 'c++11'

        return std_value

    def try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #dir already exist
            pass

        return dir
