from conans import ConanFile, CMake


class AaaConan(ConanFile):
    name = 'CNProtection'
    version = '1.0.0'
    requires = 'CNCoreUtils/1.0.0@user/testing'

    options = {
        'all_keys': [True, False]
    }
    default_options = {
        'all_keys': False
    }

    def package_info(self):
        self.output.warn("*********************************************")
        self.output.warn("************* all_keys=%s ***************" % (self.options.all_keys))
        self.output.warn("*********************************************")

