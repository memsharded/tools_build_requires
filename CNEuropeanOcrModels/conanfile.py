from conans import ConanFile, CMake

class AaaConan(ConanFile):
    name = 'CNEuropeanOcrModels'
    version = '1.0.0'
    requires = (
        'CNOcrEngine/1.0.0@user/testing'
    )
    exports_sources = '*'

    def build_requirements(self):
        model_builder = str(self.requires['CNOcrEngine']).replace('CNOcrEngine', 'CNOcrModelBuilderTool')
        self.build_requires(model_builder)
