---
name: outsystems-custom-code
description: Reference + workflow for building, testing, and deploying C# class-library "External Logic" libraries for OutSystems Developer Cloud (ODC). Covers SDK attributes ([OSInterface] / [OSAction] / [OSParameter] / [OSStructure] / [OSIgnore]), supported data types, optional parameters, logging via ILogger, project structure, runtime constraints (95s execution / 1 GB memory / 5.5 MB payload), unit + container integration tests, and deployment via the OutSystems MCP. Use when the user asks to "build a C# library for OutSystems", "create ODC external logic", "write custom code for ODC", "deploy an external library", "publish C# code to OutSystems", or names ODC External Logic / external library / OSInterface / OSAction directly.
license: MIT
compatibility: Agent-neutral workflow for Codex and Claude Code. Requires .NET 8 SDK locally; Docker for integration tests; and the `outsystems` MCP server connected and authenticated for deployment. Python is NOT required by this skill.
allowed-tools: Bash Read Write Edit mcp__outsystems__auth_status mcp__outsystems__extlib_upload mcp__outsystems__extlib_status mcp__outsystems__extlib_publish mcp__outsystems__extlib_logs mcp__outsystems__extlib_contents
metadata:
  version: "1.1.0"
  author: outsystems-r-and-d
---

# OutSystems ODC External Library Skill

This file describes how to create, build, test, and deploy C# libraries for the OutSystems Developer Cloud (ODC) External Logic feature.

---

## Project Overview

OutSystems ODC External Logic allows extending ODC apps with custom C# code. The C# class library project is built locally, published as a ZIP file to the ODC platform. OutSystems generates a wrapper around the code that exposes the decorated interfaces as server actions consumable by ODC applications.

---

## Runtime Constraints

These are hard limits enforced by the ODC platform. Never design functions that approach or exceed them:

| Constraint | Limit |
|---|---|
| Max execution duration | **95 seconds** per function call |
| Max memory | **1,024 MB** |
| Max ephemeral storage | **512 MB** |
| Max payload (inputs + outputs combined) | **5.5 MB** |

For large data: stream in chunks, use references/URLs instead of raw bytes.

---

## Project Setup

### Target Framework
- Use **.NET 8** (current ODC recommendation). Do **not** use .NET 6 for new projects.
- Project type: **Class Library** (`<OutputType>Library</OutputType>`).
- If the project is on an older .net version update to the latest version.

### Required NuGet Package
```xml
<PackageReference Include="OutSystems.ExternalLibraries.SDK" Version="1.5.0" />
```
Always use the latest stable version. Check: https://www.nuget.org/packages/OutSystems.ExternalLibraries.SDK

### Minimal `.csproj`
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="OutSystems.ExternalLibraries.SDK" Version="1.5.0" />
  </ItemGroup>
</Project>
```

---

## SDK Attributes – Core Concepts

### `[OSInterface]` – Exposes the interface to ODC
Applied to a **public interface**. Every method on this interface becomes a server action in ODC.

```csharp
using OutSystems.ExternalLibraries.SDK;

namespace MyCompany.MyLibrary
{
    [OSInterface(
        Name = "MyLibrary",
        Description = "Short description of what this library does.",
        IconResourceName = "MyCompany.MyLibrary.Resources.icon.png"
    )]
    public interface IMyLibrary
    {
        string SayHello(string name);
    }
}
```

- `Name`: The library name visible in ODC Portal. Required for ODC Forge submission.
- `Description`: Shown in ODC Portal. Required for Forge submission.
- `IconResourceName`: Embedded resource path. Required for Forge submission.

### `[OSAction]` – Customise action metadata (optional)
Applied to individual interface methods to override defaults.

```csharp
[OSAction(
    Description = "Validates an IBAN and returns structured result.",
    ReturnName = "ValidationResult",
    ReturnDescription = "The validation outcome."
)]
ValidationResult ValidateIban(string iban);
```

### `[OSParameter]` – Customise parameter metadata (optional)
```csharp
void ProcessData(
    [OSParameter(Description = "Raw input bytes", DataType = OSDataType.BinaryData)]
    byte[] data,
    [OSParameter(Description = "Output result")]
    out string result
);
```

### Optional Parameters

To make a server action parameter optional in ODC, the C# parameter **must** be both nullable **and** have a default value of `null`.

```csharp
// In interface:
[OSAction(Description = "Sends a notification")]
void SendNotification(
    [OSParameter(Description = "Recipient address")] string recipient,
    [OSParameter(Description = "Optional message subject")] string? subject = null,
    [OSParameter(Description = "Optional priority level")] int? priority = null
);

// In implementation:
public void SendNotification(string recipient, string? subject = null, int? priority = null)
{
    var resolvedSubject = subject ?? "No Subject";
    var resolvedPriority = priority ?? 0;
    // ...
}
```

**Rules to make parameter optional:**
- The parameter type must be nullable: `string?`, `int?`, `bool?`, `decimal?`, etc.
- The parameter must have `= null` as the default value in both the interface and the implementation.
- `byte[]?` (Binary Data) and struct types decorated with `[OSStructure]` can also be made optional the same way.
- `out` parameters cannot be optional.

### `[OSStructure]` – Exposes a struct as an ODC Structure
Applied to a **public struct** (not class). Used for complex input/output types.

```csharp
[OSStructure(Description = "Represents a parsed IBAN value.")]
public struct IbanResult
{
    [OSStructureField(Description = "Two-letter country code", IsMandatory = true)]
    public string Country { get; set; }

    [OSStructureField(Description = "Basic Bank Account Number")]
    public string Bban { get; set; }

    [OSStructureField(Description = "Whether the IBAN is valid")]
    public bool IsValid { get; set; }
}
```

### `[OSIgnore]` – Hides a member from ODC
Apply to methods or properties that should not be exposed as actions or structure fields.

---

## Logging
To log your custom code and generate detailed logs including informational messages and errors, you must use the Microsoft.Extensions.Logging ILogger interface in your C# code.

```csharp
using Microsoft.Extensions.Logging;
using System.Diagnostics;

namespace MyCompany
{
    public class MyLibrary : IMyLibrary
    {
        private readonly ILogger _logger;

        public MyLibrary(ILogger logger)
        {
            _logger = logger;
        }

        public string SayHello(string name, string title = "Mr./Ms.")
        {
            using var activity = Activity.Current?.Source.StartActivity("MyLibrary.SayHello");
            _logger.LogInformation($"Saying hello to {name} with title {title}");
            return $"Hello, {title} {name}";
        }

        public string SayGoodbye(string name)
        {
            using var activity = Activity.Current?.Source.StartActivity("MyLibrary.SayGoodbye");
            _logger.LogInformation($"Saying goodbye to {name}");
            return $"Goodbye, {name}";
        }
    }
}
```

---

## Supported Data Types

Only these types are valid as method parameters and return types:

| C# Type | ODC Type |
|---|---|
| `string` | Text |
| `int` | Integer |
| `long` | Long Integer |
| `bool` | Boolean |
| `decimal` | Decimal |
| `float` | Decimal |
| `double` | Decimal |
| `DateTime` | DateTime |
| `byte[]` | Binary Data |
| struct with `[OSStructure]` | Structure |
| `IEnumerable<T>` of any above | List |

**Not supported:** classes, dictionaries, nullable value types, enums (wrap in int/string), generics other than IEnumerable.

---

## Recommended Project Structure

```
MyLibrary/
├── MyLibrary.csproj
├── Interfaces/
│   └── IMyLibrary.cs          # [OSInterface]-decorated interface
├── Implementations/
│   └── MyLibrary.cs           # Class implementing the interface
├── Structures/
│   └── MyResult.cs            # [OSStructure]-decorated structs
├── Resources/
│   └── icon.png               # Embedded icon (set as EmbeddedResource)
└── Tests/
    ├── MyLibrary.UnitTests/
    │   └── MyLibraryTests.cs
    └── MyLibrary.IntegrationTests/
        └── ContainerTests.cs
```

---

## Implementation Pattern

The interface and the implementing class must be in the same assembly. ODC finds the implementation via the interface.

```csharp
// Interfaces/IMyLibrary.cs
using OutSystems.ExternalLibraries.SDK;

namespace MyCompany.MyLibrary
{
    [OSInterface(Name = "MyLibrary", Description = "Example library")]
    public interface IMyLibrary
    {
        [OSAction(Description = "Greets a person by name")]
        string Greet(
            [OSParameter(Description = "Name to greet")] string name
        );
    }
}

// Implementations/MyLibrary.cs
using Microsoft.Extensions.Logging;

namespace MyCompany.MyLibrary
{
    public class MyLibrary : IMyLibrary
    {
        private readonly ILogger _logger;

        public MyLibrary(ILogger logger)
        {
            _logger = logger;
        }

        public string Greet(string name) => $"Hello, {name}!";
    }
}
```

### Output Parameters
Use `out` parameters for multiple return values:

```csharp
// In interface:
void Parse(string input, out bool success, out string errorMessage, out MyResult result);

// In implementation:
public void Parse(string input, out bool success, out string errorMessage, out MyResult result)
{
    // ...
}
```

---

## Testing

### Unit Tests
Use standard .NET test frameworks. The library code has no ODC runtime dependency, so it can be tested directly.

```xml
<!-- MyLibrary.UnitTests.csproj -->
<PackageReference Include="xunit" Version="2.*" />
<PackageReference Include="xunit.runner.visualstudio" Version="2.*" />
<PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.*" />
<PackageReference Include="Moq" Version="4.*" />
```

```csharp
public class MyLibraryTests
{
    private readonly IMyLibrary _sut = new MyLibrary();

    [Fact]
    public void Greet_ReturnsExpectedString()
    {
        var result = _sut.Greet("World");
        Assert.Equal("Hello, World!", result);
    }
}
```

Run: `dotnet test`

### Integration Tests (Container)
Integration tests should run the code in a container matching the ODC runtime environment.

**Base image:** `mcr.microsoft.com/dotnet/aspnet:8.0`

Example `Dockerfile` for integration tests:
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish MyLibrary.IntegrationTests/MyLibrary.IntegrationTests.csproj -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "vstest", "MyLibrary.IntegrationTests.dll"]
```

Run integration tests:
```bash
docker build -t mylibrary-integration-tests .
docker run --rm mylibrary-integration-tests
```

**What to validate in integration tests:**
- All public actions execute without exceptions in the target runtime
- Memory usage stays within 1,024 MB for expected payloads
- Execution completes within 95 seconds
- Payload sizes (serialised inputs + outputs) stay under 5.5 MB

---

## Deploy

Follow the active agent's OutSystems MCP instructions for "Publish a new external library". If no OutSystems MCP server is installed, use the appropriate setup flow below.

```
On Claude Code:

Install the OutSystems outsystems-mcp plugin from OutSystems/outsystems-mcp on GitHub.
Step 1: run `claude plugin marketplace add OutSystems/outsystems-mcp`.
Step 2: run `claude plugin install outsystems@outsystems`.
Step 3: ask me for my OutSystems tenant hostname (something like `mycompany.outsystems.dev`).
Step 4: when I tell you, run `claude mcp add -s user --transport http --client-id service_studio --callback-port 7890 outsystems https://<my-tenant>/mcp` (substitute my actual tenant for `<my-tenant>`).
Step 5: tell me to restart Claude Code, then ask anything OutSystems-related; you'll drive the OAuth flow automatically via the `authenticate` tool. Do NOT tell me to run `/mcp -> outsystems -> Authenticate` manually.

On other agents, register the `outsystems` MCP server per that agent's MCP configuration and complete the OAuth flow.
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| Interface not found | Implementing class not in same assembly | Ensure interface and class are in the same `.csproj` |
| Unsupported type | Using `class` instead of `struct` for complex types | Use `struct` with `[OSStructure]` |
| ZIP structure wrong | Folder nested inside ZIP | Zip the *contents* of `/publish`, not the folder itself |
| Payload too large | Input/output exceeds 5.5 MB | Chunk data, use URLs, or split into multiple actions |
| Timeout | Single action takes more than 95 seconds | Break up long-running work; consider async chunked patterns |
| Missing icon | Forge submission fails | Embed PNG as `EmbeddedResource` and set `IconResourceName` |
