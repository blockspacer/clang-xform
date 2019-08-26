#include "MyFrontendAction.hpp"
#include "ApplyReplacements.hpp"
#include "TestingUtil.hpp"
#include "Logger.hpp"

#include <vector>
#include <string>

#include "clang/Tooling/Tooling.h"
#include "clang/Tooling/CompilationDatabase.h"

#include "gtest/gtest.h"

using namespace clang::tooling;
// This unit test compares the log file and refactored src file with corresponding baseline.
// The test is self-explained. The user does not need to make any changes here unless
// for other customizations. It is recommended to check the following few places.
// [1] dirPath: test directory path, must start with "test/"
// [2] logFile: log file name (not path), default is "sbcodexform.log"
// [3] inputFile, src file name (not path) to refactor, default is "example.cpp"

TEST(MatcherTest, __NAME__) {
  // must start with test/
  std::string dirPath/*[1]*/ = "__PATH__";
  std::string logFile/*[2]*/ = "__LOG__";
  std::string inputFile/*[3]*/ = "__FILE__";
  std::string outputFile = "tmp_output_file.yaml";
  // chdir dirPath, create outputFile, set logging properties
  int status = InitTest(dirPath, outputFile);
  ASSERT_TRUE(status);
  // setup log file
  RegisterLogFile log_file(logFile);

  std::string refactoredFile = inputFile + ".refactored";
  std::string baselineFile = inputFile + ".gold";
  std::string baselineLog = logFile + ".gold";
  std::vector<std::string> matchers = {"__NAME__"};
  std::vector<const char*> args = {__ARGS__};

  // retrieve compliation database
  std::string errMsg;
  std::unique_ptr<CompilationDatabase> compilations =
      CompilationDatabase::autoDetectFromSource(inputFile,
                                                errMsg);
  ASSERT_TRUE(compilations != nullptr);
  clang::tooling::ClangTool tool(*compilations, inputFile);
  status = tool.run(std::make_unique<MyFrontendActionFactory>(outputFile, matchers, args).get());
  ASSERT_EQ(status, 0);
  // test if matched locations are correct
  ASSERT_TRUE(CompareFiles(logFile, baselineLog));

  status = clang::replace::applyReplacements(outputFile, refactoredFile);
  ASSERT_TRUE(status);

  if (!IsEmptyFile(outputFile)) {
    // test if replacements are correct when outputFile is not empty
    ASSERT_TRUE(CompareFiles(refactoredFile, baselineFile));
  }
}