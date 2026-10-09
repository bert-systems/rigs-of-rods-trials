using System.Runtime.InteropServices;
namespace RoR.Trials;
public static class WorkerResources
{
    public const int PinnedNodes=176,PinnedBeams=744;
    public const long DetailStride=128+PinnedNodes*256+PinnedBeams*112+(PinnedNodes*4+32)*104;
    public static object DetailEstimate => new{profile="daf-detail-resources-v2",nodes=PinnedNodes,beams=PinnedBeams,
        strideBytes=DetailStride,historyBytes=DetailStride*4001,queueBytes=(3072L*1024*1024/DetailStride)*DetailStride,
        minimumAvailablePhysicalBytes=6L*1024*1024*1024,rawReservationBytes=3L*1024*1024*1024,
        reason="Whole realized pilot, all 16 node channels and endpoint beam applications; burst queue sized after retained real overflow on archive volume"};
    [StructLayout(LayoutKind.Sequential)]struct MemoryStatus {
        public uint Length,Load;
        public ulong TotalPhysical,AvailablePhysical,TotalPageFile,AvailablePageFile,TotalVirtual,AvailableVirtual,AvailableExtended;
    }
    [DllImport("kernel32.dll",SetLastError=true)]static extern bool GlobalMemoryStatusEx(ref MemoryStatus status);
    public static string? MemoryPreflight(){
        if(!OperatingSystem.IsWindows())return "Barrier detail resource profile currently supports Windows x64 only.";
        var status=new MemoryStatus{Length=(uint)Marshal.SizeOf<MemoryStatus>()};
        if(!GlobalMemoryStatusEx(ref status))return "Unable to verify available memory for the required detail buffers.";
        return status.AvailablePhysical<6ul*1024*1024*1024?"Barrier detail requires 6 GiB available physical memory including buffers and working margin; new launches held.":null;
    }
}
