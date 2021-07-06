# Install Visual Studio Build tools based on
# https://docs.microsoft.com/en-us/visualstudio/install/build-tools-container?view=vs-2019

FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019

# Download the Build Tools bootstrapper.
ADD https://aka.ms/vs/16/release/vs_buildtools.exe vs_buildtools.exe

# Install chocolatey
RUN powershell -c "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iwr https://chocolatey.org/install.ps1 -UseBasicParsing | iex"
RUN choco feature enable -n allowGlobalConfirmation

# install some tools
RUN choco install git python pypy3
RUN python -m pip install -U pip pipx pip-run

RUN setx path '%path%;C:\Users\ContainerAdministrator\.local\bin;C:\programdata\chocolatey\lib\pypy3\tools\pypy3.7-v7.3.4-win32;C:\programdata\chocolatey\lib\pypy3\tools\pypy3.7-v7.3.4-win32\Scripts'

RUN pipx install tox
RUN pipx install httpie
RUN pypy3 -m ensurepip
RUN pypy3 -m pip install -U pip

# install certificates (https://bugs.python.org/issue36137#msg336806)
RUN cmd /c 'certutil -generateSSTFromWU roots.sst && certutil -addstore -f root roots.sst && del roots.sst'


RUN setx TOX_WORK_DIR \tox

# Install Visual Studio
RUN cmd /c start /w vs_buildtools --quiet --wait --norestart --nocache modify \
 --add Microsoft.VisualStudio.Component.CoreEditor \
 --add Microsoft.VisualStudio.Workload.CoreEditor \
 --add Microsoft.VisualStudio.Component.Roslyn.Compiler \
 --add Microsoft.Component.MSBuild \
 --add Microsoft.VisualStudio.Component.TextTemplating \
 --add Microsoft.VisualStudio.Component.VC.CoreIde \
 --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 \
 --add Microsoft.VisualStudio.Component.Windows10SDK.19041 \
 --add Microsoft.VisualStudio.Component.VC.Redist.14.Latest \
 --add Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Core \
 --add Microsoft.VisualStudio.Workload.NativeDesktop \
 --add Microsoft.VisualStudio.Workload.WDExpress

RUN & \"${env:programfiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe\" -latest -prerelease -requiresAny -property installationPath -products *

RUN py -c 'from setuptools import msvc; print(msvc._msvc14_find_vc2017())'

ENTRYPOINT ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
