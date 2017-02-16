from conans import ConanFile, CMake, tools
import os
from os import path

class OpendhtConan(ConanFile):
    name        = "opendht"
    version     = "1.3.0"
    license     = "GPLv3"
    url         = "https://github.com/paulobrizolara/opendht-conan"
    repo_url    = "https://github.com/savoirfairelinux/opendht/"
    settings    = "os", "compiler", "arch"
    generators  = "cmake"
    exports     = ("CMakeLists.txt",)

    options     = {
        "shared": [True, False], 
        "build_tools" : [True, False]
    }
    default_options = (
        "shared=False", 
        "build_tools=False", 
        "msgpack-c:header_only=False"
    )

    requires = (
        "gnutls/3.4.16@DEGoodmanWilson/testing",
        "nettle/3.3@DEGoodmanWilson/testing",
        "msgpack-c/1.4.2@paulobrizolara/stable"
    )

    ZIP_URL = "%s/archive/%s.tar.gz" % (repo_url, version)
    FILE_SHA = '9a479ac3ffce481a942a7be238fe5ec3b1a5c0b9be7bdd7f11b5d0b39dec1abf'
    
    #Folder inside the zip
    INSIDE_DIR = "opendht-" + version
    UNZIPPED_DIR = "opendht"
    

    def source(self):
        zip_name = "%s.tar.gz" % self.name

        tools.download(self.ZIP_URL, zip_name)
        tools.check_sha256(zip_name, self.FILE_SHA)
        tools.untargz(zip_name)
        #os.unlink(zip_name)
        
        os.rename(self.INSIDE_DIR, self.UNZIPPED_DIR)

    def build(self):
        #Make build dir
        build_dir = self.try_make_dir(os.path.join(".", "build"))

        #Change to build dir
        os.chdir(build_dir)

        cmake = CMake(self.settings)
        
        self.cmake_configure(cmake)
        self.cmake_build_and_install(cmake)
        
    def package(self):
        # copy only include files, because lib files should be installed by cmake
        self.copy("**.h", src=path.join(self.UNZIPPED_DIR, "include"), dst="include", keep_path=True)

    def package_info(self):
        self.cpp_info.libs      = ["opendht"]

        # add dependency includes
        self.cpp_info.includedirs += self.deps_cpp_info["msgpack-c"].include_paths
        self.cpp_info.includedirs += self.deps_cpp_info["gnutls"].include_paths

        # add dependency libs
        for lib in ("gnutls", "nettle", "libiconv", "gmp", "gnutls", "zlib"):
            self.cpp_info.libdirs     += self.deps_cpp_info[lib].lib_paths
            self.cpp_info.libs        += self.deps_cpp_info[lib].libs


####################################### Helpers ################################################

    def cmake_configure(self, cmake):    
        src_dir = self.conanfile_directory
        cmake_cmd = 'cmake "%s" %s %s' % (src_dir, cmake.command_line, self.cmake_args())
        
        self.output.info(cmake_cmd)
        self.run(cmake_cmd)
        
    def cmake_build_and_install(self, cmake):
        self.run('cmake --build . --target install %s' % cmake.build_config)
        
    def cmake_args(self):
        """Generate arguments for cmake"""

        if not hasattr(self, 'package_folder'):
            self.package_folder = "dist"

        args = [
                self.cmake_bool_option("OPENDHT_SHARED", self.options.shared),
                self.cmake_bool_option("OPENDHT_STATIC", not self.options.shared),
                self.cmake_bool_option("OPENDHT_TOOLS"    , self.options.build_tools)
        ]
        args += [
            '-DCMAKE_INSTALL_PREFIX="%s"' % self.package_folder,
            '-DCMAKE_INSTALL_LIBDIR="lib"'
        ]

        return ' '.join(args)

    def cmake_bool_option(self, name, value):
        return "-D%s=%s" % (name.upper(), "ON" if value else "OFF");

    def try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #dir already exist
            pass

        return dir
