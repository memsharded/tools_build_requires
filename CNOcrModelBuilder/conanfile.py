from conans import ConanFile, CMake


class AaaConan(ConanFile):
    name = 'CNOcrModelBuilder'
    version = '1.0.0'
    requires = (
        'CNCoreUtils/1.2.0@user/testing',
        'CNOcrEngine/1.0.0@user/testing',
        'CNProtection/1.0.0@user/testing',
    )

    def configure(self):
        self.options['CNProtection'].all_keys = True

