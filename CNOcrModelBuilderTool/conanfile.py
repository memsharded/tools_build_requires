from conans import ConanFile, CMake


class AaaConan(ConanFile):
    name = 'CNOcrModelBuilderTool'
    version = '1.0.0'
    build_requires = (
        'CNOcrModelBuilder/%s@user/testing' % version,
    )

    def package(self):
        # Do repackage artifacts from ModelBuilder
        pass


    

