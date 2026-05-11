using System;
using System.Diagnostics;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Windows.Forms;

namespace SimpleAINovelAppLauncher
{
    internal static class Program
    {
        [STAThread]
        private static int Main()
        {
            try
            {
                string exeDir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
                if (string.IsNullOrEmpty(exeDir))
                {
                    exeDir = Environment.CurrentDirectory;
                }
                string installDir = Path.Combine(exeDir, "runtime", LauncherConfig.Version);
                string dataDir = Path.Combine(exeDir, "data");

                Directory.CreateDirectory(installDir);
                Directory.CreateDirectory(dataDir);
                ExtractPayload(installDir);

                if (Environment.GetEnvironmentVariable("SIMPLE_AI_NOVEL_LAUNCHER_EXTRACT_ONLY") == "1")
                {
                    return 0;
                }

                string pythonw = Path.Combine(installDir, "python", "pythonw.exe");
                string mainScript = Path.Combine(installDir, "app", "main.py");
                if (!File.Exists(pythonw) || !File.Exists(mainScript))
                {
                    throw new FileNotFoundException("Runtime files are incomplete.");
                }

                ProcessStartInfo startInfo = new ProcessStartInfo();
                startInfo.FileName = pythonw;
                startInfo.Arguments = Quote(mainScript);
                startInfo.WorkingDirectory = Path.Combine(installDir, "app");
                startInfo.UseShellExecute = false;

                Environment.SetEnvironmentVariable("SIMPLE_AI_NOVEL_DATA_DIR", dataDir);
                Environment.SetEnvironmentVariable("PYTHONHOME", Path.Combine(installDir, "python"));
                Environment.SetEnvironmentVariable("PYTHONPATH", "");
                Process.Start(startInfo);
                return 0;
            }
            catch (Exception exc)
            {
                try
                {
                    Console.Error.WriteLine(exc.ToString());
                }
                catch
                {
                    // The windowed launcher has no console; keep the message box as the visible fallback.
                }
                MessageBox.Show(
                    exc.Message,
                    LauncherConfig.AppName + " startup failed",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Error
                );
                return 1;
            }
        }

        private static void ExtractPayload(string installDir)
        {
            string tempZip = Path.Combine(
                Path.GetTempPath(),
                LauncherConfig.AppName + "-" + LauncherConfig.Version + "-" + Guid.NewGuid().ToString("N") + ".zip"
            );

            try
            {
                using (Stream source = Assembly.GetExecutingAssembly().GetManifestResourceStream("payload.zip"))
                {
                    if (source == null)
                    {
                        throw new InvalidOperationException("Embedded payload.zip was not found.");
                    }
                    using (FileStream target = new FileStream(tempZip, FileMode.Create, FileAccess.Write))
                    {
                        source.CopyTo(target);
                    }
                }

                using (ZipArchive archive = ZipFile.OpenRead(tempZip))
                {
                    foreach (ZipArchiveEntry entry in archive.Entries)
                    {
                        ExtractEntry(entry, installDir);
                    }
                }
            }
            finally
            {
                try
                {
                    if (File.Exists(tempZip))
                    {
                        File.Delete(tempZip);
                    }
                }
                catch
                {
                    // Best-effort cleanup only.
                }
            }
        }

        private static void ExtractEntry(ZipArchiveEntry entry, string installDir)
        {
            string relativePath = entry.FullName.Replace('/', Path.DirectorySeparatorChar);
            if (string.IsNullOrWhiteSpace(relativePath))
            {
                return;
            }

            string destination = Path.GetFullPath(Path.Combine(installDir, relativePath));
            string root = Path.GetFullPath(installDir + Path.DirectorySeparatorChar);
            if (!destination.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Blocked unsafe payload path: " + entry.FullName);
            }

            if (string.IsNullOrEmpty(entry.Name))
            {
                Directory.CreateDirectory(destination);
                return;
            }

            string parent = Path.GetDirectoryName(destination);
            if (!string.IsNullOrEmpty(parent))
            {
                Directory.CreateDirectory(parent);
            }

            using (Stream input = entry.Open())
            using (FileStream output = new FileStream(destination, FileMode.Create, FileAccess.Write))
            {
                input.CopyTo(output);
            }
        }

        private static string Quote(string value)
        {
            return "\"" + value.Replace("\"", "\\\"") + "\"";
        }
    }
}
