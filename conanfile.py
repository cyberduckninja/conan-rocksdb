from conans import ConanFile, CMake, tools
import os


class RocksdbConan(ConanFile):
    name = "rocksdb"
    version = "6.8.1"
    license = "https://github.com/facebook/rocksdb/blob/master/COPYING"
    url = "https://github.com/jinncrafters/conan-rocksdb"
    description = "A library that provides an embeddable, persistent key-value store for fast storage."
    settings = "os", "compiler", "build_type", "arch"

    generators = "cmake"
    build_policy = "missing"
    _cmake = None
    generators = "cmake", "cmake_find_package"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
    }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    requires = (
        # TODO snappy, zstandard
        "gflags/2.2.2",
        "zlib/1.2.11@conan/stable",
        "bzip2/1.0.6@conan/stable",
        "lz4/1.9.2"
    )

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(
            os.path.join(self.source_folder, self._source_subfolder, "CMakeLists.txt"),
            "include(CMakeDependentOption)",
            '''
            if (EXISTS ${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
                conan_basic_setup()
            else ()
                message(WARNING "The file conanbuildinfo.cmake doesn't exist, you have to run conan install first")
            endif ()
            include(CMakeDependentOption)
            ''')

    def _configure_cmake(self):
        if not self._cmake:
            self._cmake = CMake(self)
            self._cmake.definitions["WITH_BENCHMARK_TOOLS"] = False  # example
            self._cmake.configure(source_dir=self._source_subfolder)
        return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.Apache", src=self._source_subfolder, keep_path=False)
        self.copy("LICENSE.leveldb", src=self._source_subfolder, keep_path=False)

        self.copy("*.h", dst="include", src=("%s/include" % self._source_subfolder))

        if self.options.shared:
            self.copy("librocksdb.so", dst="lib", src=self._source_subfolder, keep_path=False)
        else:
            self.copy("librocksdb.a", dst="lib", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["rocksdb"]
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
