#!/usr/bin/python3

# Copyright (C) 2019-2021 Julian Valentin, LTeX Development Community
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import argparse
import json
import pathlib
import platform
import re
import shlex
import subprocess
import sys
import tarfile
from typing import Optional
import urllib.error
import urllib.parse
import urllib.request
import zipfile

import semver

sys.path.append(str(pathlib.Path(__file__).parent))
import common



libDirPath = common.repoDirPath.joinpath("lib")



def cleanLibDir() -> None:
  cmd = ["git", "-C", str(common.repoDirPath), "clean", "-f", "-x", str(libDirPath)]
  print("Cleaning lib/ by running '{}'...".format(" ".join(shlex.quote(x) for x in cmd)))
  subprocess.run(cmd)



def getLtexVersion() -> semver.VersionInfo:
  with open(common.repoDirPath.joinpath("package.json"), "r") as f: packageJson = json.load(f)
  return semver.VersionInfo.parse(packageJson["version"])



def downloadLtexLs(platform: str, arch: str) -> None:
  ltexLsArchiveType = ("zip" if platform == "windows" else "tar.gz")
  ltexLsArchiveName = (
      f"ltex-ls-{common.toBeDownloadedLtexLsVersion}-{platform}-{arch}.{ltexLsArchiveType}")

  ltexLsUrl = ("https://github.com/valentjn/ltex-ls/releases/download/"
      f"{common.toBeDownloadedLtexLsTag}/{ltexLsArchiveName}")
  ltexLsArchivePath = libDirPath.joinpath(ltexLsArchiveName)
  print(f"Downloading ltex-ls {common.toBeDownloadedLtexLsVersion} from '{ltexLsUrl}' to "
      f"'{ltexLsArchivePath}'...")
  urllib.request.urlretrieve(ltexLsUrl, ltexLsArchivePath)

  extractLtexLs(ltexLsArchivePath)

  print("Removing ltex-ls archive...")
  ltexLsArchivePath.unlink()

def extractLtexLs(ltexLsArchivePath: pathlib.Path) -> None:
  print("Extracting ltex-ls archive...")

  if ltexLsArchivePath.suffix == ".zip":
    with zipfile.ZipFile(ltexLsArchivePath, "r") as zipFile: zipFile.extractall(path=libDirPath)
  else:
    with tarfile.open(ltexLsArchivePath, "r:gz") as tarFile: tarFile.extractall(path=libDirPath)



def createPackage(ltexPlatform: Optional[str] = None, ltexArch: Optional[str] = None) -> None:
  ltexVersion = getLtexVersion()

  if ltexPlatform is None:
    packageName = f"vscode-ltex-{ltexVersion}.vsix"
  else:
    packageName = f"vscode-ltex-{ltexVersion}-offline-{ltexPlatform}-{ltexArch}.vsix"

  assert re.match(r"^[\-\.0-9A-Z_a-z]+$", packageName) is not None
  cmd = f"npx vsce package -o \"{packageName}\""
  print(f"Creating package by running '{cmd}'...")
  subprocess.run(cmd, shell=True)



def main() -> None:
  parser = argparse.ArgumentParser(description="Build offline packages of LTeX")
  parser.add_argument("--current-system", action="store_true",
      help="Build offline package only for current platform/architecture")
  parser.add_argument("--ltex-ls-path", type=pathlib.Path, metavar="PATH",
      help="Don't download ltex-ls from GitHub, but use archive from this path")
  args = parser.parse_args()

  if args.current_system:
    ltexPlatform = {
          "Linux" : "linux",
          "Darwin" : "mac",
          "Windows" : "windows",
        }[platform.system()]
    ltexArch = {
          "AMD64" : "x64",
          "x86_64" : "x64",
        }[platform.machine()]
    ltexPlatformArchs = [(ltexPlatform, ltexArch)]
  else:
    ltexPlatformArchs = [("linux", "x64"), ("mac", "x64"), ("windows", "x64")]

  ltexLsArchivePath = args.ltex_ls_path
  cleanLibDir()

  for ltexPlatform, ltexArch in ltexPlatformArchs:
    print("")
    print(f"Processing platform '{ltexPlatform}' and architecture '{ltexArch}'...")

    if ltexLsArchivePath is None:
      downloadLtexLs(ltexPlatform, ltexArch)
    else:
      extractLtexLs(ltexLsArchivePath)

    createPackage(ltexPlatform, ltexArch)
    cleanLibDir()



if __name__ == "__main__":
  main()
