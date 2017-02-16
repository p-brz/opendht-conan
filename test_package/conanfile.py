from conans import ConanFile, CMake
import os


username = os.getenv("CONAN_USERNAME", "paulobrizolara")
channel = os.getenv("CONAN_CHANNEL", "testing")
version = "1.2.1"
package = "opendht"

class claraTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    requires = "%s/%s@%s/%s" % (package, version, username, channel)
    generators = "cmake"

    def build(self):
	cmake = CMake(self.settings)
        self.run('cmake "%s" %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def imports(self):
        self.copy("*.dll", "bin", "bin")
        self.copy("*.dylib", "bin", "bin")

    def test(self):
        self.run(os.path.join("bin","example"))
