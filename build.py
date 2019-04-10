import os


def run(cmd):
    ret = os.system(cmd)
    if ret != 0:
        raise Exception(cmd)

run("cd CNCoreUtils && conan create . CNCoreUtils/1.0.0@user/testing")
run("cd CNCoreUtils && conan create . CNCoreUtils/1.1.0@user/testing")
run("cd CNCoreUtils && conan create . CNCoreUtils/1.2.0@user/testing")
run("cd CNProtection && conan create . user/testing")
run("cd CNProtection && conan create . user/testing -o CNProtection:all_keys=True")
run("cd CNOcrEngine && conan create . user/testing")
run("cd CNOcrModelBuilder && conan create . user/testing")
run("cd CNOcrModelBuilderTool && conan create . user/testing")
run("cd CNEuropeanOcrModels && conan create . user/testing")
run("cd CNFinalProduct && conan install .")