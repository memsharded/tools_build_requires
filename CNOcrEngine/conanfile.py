from conans import ConanFile, CMake

class AaaConan(ConanFile):
    name = 'CNOcrEngine'
    version = '1.0.0'
    requires = (
        'CNCoreUtils/1.1.0@user/testing',
        'CNProtection/1.0.0@user/testing',
    )

    def configure(self):
        self.options['CNProtection'].all_keys = False

