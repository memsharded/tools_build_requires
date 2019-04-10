# tools_build_requires


Lets start with this part of the graph:

![image](https://user-images.githubusercontent.com/15367152/55870318-9a110f80-5b88-11e9-9b36-f2f0a85b17d7.png)


Some pre-conditions:
- The OCRModelBuilder EXE can only link with one version and configuration of all the other static libraries.
- If at some point the dependency graph of OCRModelBuilder has two different versions or two different configurations (like all_keys=True and all_keys=False) of the same dependency, that is a conflict, and an error should be raised, and the build should not continue as the final result would be buggy, as it is not determined which package version and configuration will be linked

The expansion of the graph IF OcrModelBuilder uses build_requires as currently defined would be something like:

![image](https://user-images.githubusercontent.com/15367152/55871321-b746dd80-5b8a-11e9-8a6d-8bd7b1917431.png)

This graph had 2 important bugs in conan 1.12 and older versions:
- There are several versions of CoreUtils that try to be linked in the Exe. Which version was finally being used was not deterministic and totally quiet, the different versions of CoreUtils were dumping their information in ``deps_cpp_info``, and only the last version that did it was the one finally used.
- There can be different configurations of the Protection package doing the same overwrite. If the consumer package OcrModelBuilder didn't explicitly change the ``all_keys``, there would be 2 different configurations, and the one finally being used was also not deterministic.

With the new expansion model defined in Conan 1.13, those bugs have been fixed. Conflicts will be raised, and the final dependency graph when the conflicts are solved, will resemble the first figure, with diamonds. So far, this behavior is not a considered a regression and it won't be reverted, the conflicts totally make sense and are the evidence of something that in the past was failing silently. I am not saying that in some cases the final result couldn't be a good one, but that was mostly a lucky coincidence.

Now the problem is that ``build_requires`` do not behave like normal requires. They do not override the same way, because they are essentially private to the package that declares them. If you want to make them work correctly, you need to correctly align the versions used in the different packages requires and build requires. I think the underlying cause of this discussion is the abuse of ``build_requires`` trying to approach a different use case that the one they were designed for. Please let me summarize some critical points from the docs:

> - There are requirements that are only needed when you need to build a package from sources, but if the binary package already exists, you don’t want to install or retrieve them.
> - These could be dev tools, compilers, build systems, code analyzers, testing libraries, etc.
> - They can be very orthogonal to the creation of the package. It doesn’t matter whether you build zlib with CMake 3.4, 3.5 or 3.6. As long as the CMakeLists.txt is compatible, it will produce the same final package.
> - Build requirements do not affect the binary package ID. If using a different build requirement produces a different binary, you should consider adding an option or a setting to model that (if not already modeled).
> 

That means, they are designed for tools like cmake or gtest. Not for libraries to be linked with. They shouldn't affect at all to your binary. It doesn't matter if you are using the CMake from your system, or from a Conan package, and it doesn't matter if you are building your tests linked with gtest or not, the final package (headers, library), should be the same.

This is definitely not the case for an executable linking with libraries. They are really required, they affect the binary, they are not tools that will be installed in the system. Another view, would be what happens if now the libraries are shared instead of static. Then, a ``build_require`` will not work, as the dependencies are necessary not only at build time, but also at consume time. That could be addressed with some conditional logic that uses ``build_requires`` if the some option is ``shared=False``, and regular ``requires`` if the option is ``shared=True``, but that construct would be a clear smell.

So, the first stopper, which is building OcrModelBuilder is solved if we use regular requires instead of build_requires in it. Now the problem is moved downstream when we want to use this OcrModelBuilder as a build_require for EuropeanOcrModels, which is trying to do:

![image](https://user-images.githubusercontent.com/15367152/55875344-29bcbb00-5b95-11e9-96cb-23baf0dd7e23.png)

The different versions of CoreUtils and the different configurations of Protection (with and without all_keys) will conflict, because EuropeanOcrModels need to build, it will ``build_require`` OcrModelBuilder, and that will transitively try to plug the incompatible dependencies.

So, what could be a possible approach right now, with the current provided tools? I think you already realized that 2 levels of ``build_requires`` is what it is really needed to fully isolate dependencies when they are joined at build time in the same package, coming both from the regular requires and from build_requires. So, as all problems in SW Engineering, I'd say this could be approached adding a level of indirection:

- The code is in the github repo: https://github.com/memsharded/tools_build_requires. 
- It defines a OcrModelBuilderTool that repackages the OcrModelBuilder, according to: https://docs.conan.io/en/latest/devtools/running_packages.html#runtime-packages-and-re-packaging
- The OcrModelBuilderTool could probably define ``settings = "os_build", "arch_build"`` for correct cross-building, and isolating the build settings (a single OcrModelBuilderTool executable could be valid for different release/debug and compiler versions settings)

The graph would be:

![image](https://user-images.githubusercontent.com/15367152/55875860-676e1380-5b96-11e9-95a4-7fa3fa0b938c.png)

This approach has some other nice properties:
- The OcrModelBuilder would contain only the executable. 
- The OcrModelBuilderTool package will repackage the executable, but it might be able for example to repackage the shared libraries, if the option ``shared=True`` was used to build the OcrModelBuilder.
- The result would be an independent OcrModelBuilderTool that can be used in the same way a CMake package would be use.

Please check the repo at https://github.com/memsharded/tools_build_requires, it implements exactly this later graph

So, in my opinion, the changes introduced in Conan 1.13 and maintained in Conan 1.14, (modulo the bug fix pending for Conan 1.14.2 in https://github.com/conan-io/conan/pull/4937) are valid, and actually protecting from very dangerous effects of abuse of build-requires, like linking the wrong dependency version, or what could be worse, to link with the wrong ``all_keys=True`` option in production without even noticing.

Now, it is true that a mechanism to be able to depend on tools with build_requires, when those tools also have transitive and incompatible dependencies with our main dependency graph is necessary.
I think the possible approach with current tools is the creation of a dedicated "Tool" re-package. Also, this should probably be the point where a new model is necessary, to specify that EuropeanOcrModels depends as ``build_require`` to OcrModelBuilder, AND that it doesn't need its transitive dependencies. Or maybe a characteristic in OcrModelBuilder, that marks the package as a "Tool", and it knows how to model that regarding the transitivity. Those are very preliminary ideas, and it would be a complicated thing, but I feel that the real solution goes in this direction.


