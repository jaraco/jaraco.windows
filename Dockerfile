# Install Visual Studio Build tools based on
# https://docs.microsoft.com/en-us/visualstudio/install/build-tools-container?view=vs-2019

FROM mcr.microsoft.com/dotnet/framework/sdk:4.8-windowsservercore-ltsc2019

# Download the Build Tools bootstrapper.
ADD https://aka.ms/vs/16/release/vs_buildtools.exe vs_buildtools.exe

# Install Build Tools with the Microsoft.VisualStudio.Workload.AzureBuildTools workload.
# Exclude workloads and components with known issues.
RUN ./vs_buildtools.exe --quiet --wait --norestart --nocache --installPath C:\BuildTools --add Microsoft.VisualStudio.Workload.AzureBuildTools --remove Microsoft.VisualStudio.Component.Windows10SDK.10240 --remove Microsoft.VisualStudio.Component.Windows10SDK.10586 --remove Microsoft.VisualStudio.Component.Windows10SDK.14393 --remove Microsoft.VisualStudio.Component.Windows81SDK

ENTRYPOINT ["powershell.exe", "-NoLogo", "-ExecutionPolicy", "Bypass"]
