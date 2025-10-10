import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AlertCircle, Monitor, Thermometer, Zap, Activity, Settings, Shield, HardDrive } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface NvidiaGPU {
  name: string;
  memory_total: number;
  memory_used: number;
  temperature: number;
  power_draw: number;
}

interface GPUInfo {
  nvidia: {
    available: boolean;
    gpus: NvidiaGPU[];
  };
  amd: {
    available: boolean;
    info: string;
  };
  intel: {
    available: boolean;
    info: string;
  };
  general: {
    devices: string[];
  };
}

export default function GPUManager() {
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [output, setOutput] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [gpuInfo, setGpuInfo] = useState<GPUInfo | null>(null);
  const [selectedGPU, setSelectedGPU] = useState<number>(0);

  // Simulated API calls - replace with actual backend calls
  const fetchGPUInfo = async (): Promise<GPUInfo> => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    return {
      nvidia: {
        available: true,
        gpus: [
          {
            name: "NVIDIA GeForce RTX 4080",
            memory_total: 16384,
            memory_used: 2048,
            temperature: 42,
            power_draw: 85.5
          },
          {
            name: "NVIDIA GeForce RTX 3060",
            memory_total: 12288,
            memory_used: 1024,
            temperature: 38,
            power_draw: 45.2
          }
        ]
      },
      amd: {
        available: false,
        info: ""
      },
      intel: {
        available: true,
        info: "Intel UHD Graphics 770"
      },
      general: {
        devices: [
          "00:02.0 VGA compatible controller: Intel Corporation Device 4692 (rev 0c)",
          "01:00.0 VGA compatible controller: NVIDIA Corporation GA104 [GeForce RTX 4080] (rev a1)"
        ]
      }
    };
  };

  const setGPUPowerLimit = async (limit: number): Promise<{success: boolean, error?: string}> => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return Math.random() > 0.1 ? {success: true} : {success: false, error: "Failed to set power limit"};
  };

  const setGPUMemoryClock = async (clock: number): Promise<{success: boolean, error?: string}> => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return Math.random() > 0.1 ? {success: true} : {success: false, error: "Failed to set memory clock"};
  };

  const setGPUFanSpeed = async (speed: number): Promise<{success: boolean, error?: string}> => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return Math.random() > 0.1 ? {success: true} : {success: false, error: "Failed to set fan speed"};
  };

  // Load GPU info on component mount
  useEffect(() => {
    const loadGPUInfo = async () => {
      try {
        setLoading(true);
        const info = await fetchGPUInfo();
        setGpuInfo(info);
      } catch (err) {
        setError("Failed to load GPU information");
      } finally {
        setLoading(false);
      }
    };

    loadGPUInfo();
  }, []);

  const handleOptionSelect = async (value: string) => {
    setSelectedOption(value);
    setOutput("");
    setError("");

    if (value === "1" && gpuInfo) {
      let infoText = "=== GPU System Information ===\n\n";
      
      if (gpuInfo.nvidia.available) {
        infoText += "NVIDIA GPUs:\n";
        gpuInfo.nvidia.gpus.forEach((gpu, index) => {
          infoText += `  GPU ${index}: ${gpu.name}\n`;
          infoText += `    Memory: ${gpu.memory_used}MB / ${gpu.memory_total}MB\n`;
          infoText += `    Temperature: ${gpu.temperature}°C\n`;
          infoText += `    Power Draw: ${gpu.power_draw}W\n\n`;
        });
      }
      
      if (gpuInfo.intel.available) {
        infoText += `Intel GPU: ${gpuInfo.intel.info}\n\n`;
      }
      
      if (gpuInfo.amd.available) {
        infoText += `AMD GPU Information:\n${gpuInfo.amd.info}\n\n`;
      }
      
      infoText += "Detected Graphics Devices:\n";
      gpuInfo.general.devices.forEach(device => {
        infoText += `  ${device}\n`;
      });
      
      setOutput(infoText);
    }
  };

  const getMemoryUsagePercentage = (gpu: NvidiaGPU): number => {
    return (gpu.memory_used / gpu.memory_total) * 100;
  };

  const getThermalStatus = (temperature: number): { color: string; status: string } => {
    if (temperature < 40) return { color: "text-blue-600", status: "Cool" };
    if (temperature < 60) return { color: "text-green-600", status: "Normal" };
    if (temperature < 80) return { color: "text-yellow-600", status: "Warm" };
    return { color: "text-red-600", status: "Hot" };
  };

  const getPowerStatus = (powerDraw: number): { color: string; status: string } => {
    if (powerDraw < 50) return { color: "text-green-600", status: "Low" };
    if (powerDraw < 150) return { color: "text-yellow-600", status: "Moderate" };
    return { color: "text-red-600", status: "High" };
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2" role="heading" aria-level={1}>
            <Monitor className="h-6 w-6" aria-hidden="true" />
            GPU Management System
            <Shield className="h-5 w-5 text-green-600" aria-label="Secure system" />
          </CardTitle>
        </CardHeader>
      </Card>

      {/* GPU Overview */}
      {gpuInfo && (
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="nvidia" disabled={!gpuInfo.nvidia.available}>
              NVIDIA {gpuInfo.nvidia.available && <Badge variant="secondary" className="ml-1">{gpuInfo.nvidia.gpus.length}</Badge>}
            </TabsTrigger>
            <TabsTrigger value="intel" disabled={!gpuInfo.intel.available}>Intel</TabsTrigger>
            <TabsTrigger value="amd" disabled={!gpuInfo.amd.available}>AMD</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" aria-hidden="true" />
                  System Graphics Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {gpuInfo.nvidia.available && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium flex items-center gap-2">
                        <Badge variant="outline">NVIDIA</Badge>
                        Graphics Cards
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        {gpuInfo.nvidia.gpus.length} device(s) detected
                      </p>
                    </div>
                  )}
                  
                  {gpuInfo.intel.available && (
                    <div className="space-y-2">
                      <Label className="text-sm font-medium flex items-center gap-2">
                        <Badge variant="outline">Intel</Badge>
                        Integrated Graphics
                      </Label>
                      <p className="text-sm text-muted-foreground">Available</p>
                    </div>
                  )}
                  
                  <div className="space-y-2">
                    <Label className="text-sm font-medium">Total Devices</Label>
                    <p className="text-sm text-muted-foreground">
                      {gpuInfo.general.devices.length} graphics device(s)
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* NVIDIA Tab */}
          <TabsContent value="nvidia" className="space-y-4">
            {gpuInfo.nvidia.available && (
              <>
                {/* GPU Selection */}
                {gpuInfo.nvidia.gpus.length > 1 && (
                  <Card>
                    <CardHeader>
                      <CardTitle>GPU Selection</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Select value={selectedGPU.toString()} onValueChange={(value) => setSelectedGPU(parseInt(value))}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select GPU" />
                        </SelectTrigger>
                        <SelectContent>
                          {gpuInfo.nvidia.gpus.map((gpu, index) => (
                            <SelectItem key={index} value={index.toString()}>
                              GPU {index}: {gpu.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </CardContent>
                  </Card>
                )}

                {/* Current GPU Status */}
                {gpuInfo.nvidia.gpus[selectedGPU] && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Monitor className="h-5 w-5" aria-hidden="true" />
                        {gpuInfo.nvidia.gpus[selectedGPU].name}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Memory Usage */}
                        <div className="space-y-3">
                          <Label className="text-sm font-medium flex items-center gap-2">
                            <HardDrive className="h-4 w-4" aria-hidden="true" />
                            Video Memory
                          </Label>
                          <div className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span>Used: {gpuInfo.nvidia.gpus[selectedGPU].memory_used}MB</span>
                              <span>Total: {gpuInfo.nvidia.gpus[selectedGPU].memory_total}MB</span>
                            </div>
                            <Progress 
                              value={getMemoryUsagePercentage(gpuInfo.nvidia.gpus[selectedGPU])} 
                              className="w-full"
                              aria-label={`Memory usage: ${getMemoryUsagePercentage(gpuInfo.nvidia.gpus[selectedGPU]).toFixed(1)}%`}
                            />
                            <p className="text-xs text-muted-foreground">
                              {getMemoryUsagePercentage(gpuInfo.nvidia.gpus[selectedGPU]).toFixed(1)}% utilized
                            </p>
                          </div>
                        </div>

                        {/* Temperature */}
                        <div className="space-y-3">
                          <Label className="text-sm font-medium flex items-center gap-2">
                            <Thermometer className="h-4 w-4" aria-hidden="true" />
                            Temperature
                          </Label>
                          <div className="space-y-2">
                            <div className={`text-2xl font-bold ${getThermalStatus(gpuInfo.nvidia.gpus[selectedGPU].temperature).color}`}>
                              {gpuInfo.nvidia.gpus[selectedGPU].temperature}°C
                            </div>
                            <Badge variant="outline">
                              {getThermalStatus(gpuInfo.nvidia.gpus[selectedGPU].temperature).status}
                            </Badge>
                            <Progress 
                              value={Math.min((gpuInfo.nvidia.gpus[selectedGPU].temperature / 100) * 100, 100)} 
                              className="w-full"
                              aria-label={`GPU temperature: ${gpuInfo.nvidia.gpus[selectedGPU].temperature}°C`}
                            />
                          </div>
                        </div>

                        {/* Power Draw */}
                        <div className="space-y-3">
                          <Label className="text-sm font-medium flex items-center gap-2">
                            <Zap className="h-4 w-4" aria-hidden="true" />
                            Power Consumption
                          </Label>
                          <div className="space-y-2">
                            <div className={`text-xl font-semibold ${getPowerStatus(gpuInfo.nvidia.gpus[selectedGPU].power_draw).color}`}>
                              {gpuInfo.nvidia.gpus[selectedGPU].power_draw}W
                            </div>
                            <Badge variant="outline">
                              {getPowerStatus(gpuInfo.nvidia.gpus[selectedGPU].power_draw).status} Power
                            </Badge>
                          </div>
                        </div>

                        {/* GPU Utilization (simulated) */}
                        <div className="space-y-3">
                          <Label className="text-sm font-medium">GPU Utilization</Label>
                          <div className="space-y-2">
                            <Progress 
                              value={45} 
                              className="w-full"
                              aria-label="GPU utilization: 45%"
                            />
                            <p className="text-xs text-muted-foreground">45% GPU load</p>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            )}
          </TabsContent>

          {/* Intel Tab */}
          <TabsContent value="intel" className="space-y-4">
            {gpuInfo.intel.available && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Monitor className="h-5 w-5" aria-hidden="true" />
                    Intel Integrated Graphics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="p-4 bg-muted rounded-md">
                      <p className="text-sm font-mono">{gpuInfo.intel.info}</p>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Intel integrated graphics detected. Advanced management features may require additional tools.
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* AMD Tab */}
          <TabsContent value="amd" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5" aria-hidden="true" />
                  AMD Graphics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  No AMD graphics cards detected. Install ROCm tools for AMD GPU management.
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}

      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" aria-hidden="true" />
            GPU Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Operation Selection */}
          <div className="space-y-2">
            <Label htmlFor="gpu-operation-select">Select Operation</Label>
            <Select 
              onValueChange={handleOptionSelect} 
              value={selectedOption}
              disabled={loading}
            >
              <SelectTrigger id="gpu-operation-select" aria-label="Select GPU operation">
                <SelectValue placeholder="Choose a GPU management operation" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Show GPU Information</SelectItem>
                <SelectItem value="2">Set Power Limit</SelectItem>
                <SelectItem value="3">Set Memory Clock</SelectItem>
                <SelectItem value="4">Set Fan Speed</SelectItem>
                <SelectItem value="5">GPU Stress Test</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          {/* GPU Controls based on selection */}
          {selectedOption === "2" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="power-limit-input">Power Limit (Watts)</Label>
                <Input
                  id="power-limit-input"
                  placeholder="Enter power limit (e.g., 200)"
                  disabled={loading}
                />
                <p className="text-sm text-muted-foreground">
                  Typical range: 50W - 450W depending on GPU model
                </p>
              </div>
              <Button 
                disabled={loading}
                className="w-full md:w-auto"
                aria-label="Set GPU power limit"
              >
                {loading ? "Setting Power Limit..." : "Set Power Limit"}
              </Button>
            </div>
          )}

          {selectedOption === "3" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="memory-clock-input">Memory Clock (MHz)</Label>
                <Input
                  id="memory-clock-input"
                  placeholder="Enter memory clock (e.g., 1750)"
                  disabled={loading}
                />
                <p className="text-sm text-muted-foreground">
                  Adjust memory clock frequency. Use caution with overclocking.
                </p>
              </div>
              <Button 
                disabled={loading}
                className="w-full md:w-auto"
                aria-label="Set GPU memory clock"
              >
                {loading ? "Setting Memory Clock..." : "Set Memory Clock"}
              </Button>
            </div>
          )}

          {selectedOption === "4" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="fan-speed-input">Fan Speed (%)</Label>
                <Input
                  id="fan-speed-input"
                  placeholder="Enter fan speed percentage (0-100)"
                  disabled={loading}
                />
                <p className="text-sm text-muted-foreground">
                  Manual fan control. Use 'auto' to return to automatic control.
                </p>
              </div>
              <Button 
                disabled={loading}
                className="w-full md:w-auto"
                aria-label="Set GPU fan speed"
              >
                {loading ? "Setting Fan Speed..." : "Set Fan Speed"}
              </Button>
            </div>
          )}

          {selectedOption === "5" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>GPU Stress Test</Label>
                <p className="text-sm text-muted-foreground">
                  Run a comprehensive GPU stress test to check stability and thermal performance.
                </p>
              </div>
              
              <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <AlertCircle className="h-4 w-4 text-yellow-600" aria-hidden="true" />
                <span className="text-sm text-yellow-800">
                  Warning: GPU stress testing will increase temperature and power consumption significantly
                </span>
              </div>
              
              <Button 
                disabled={loading}
                className="w-full md:w-auto"
                variant="outline"
                aria-label="Run GPU stress test"
              >
                <Zap className="h-4 w-4 mr-2" aria-hidden="true" />
                {loading ? "Running Test..." : "Run GPU Stress Test"}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Results Display */}
      {(output || error) && (
        <Card>
          <CardHeader>
            <CardTitle>Results</CardTitle>
          </CardHeader>
          <CardContent>
            {output && (
              <div className="p-4 bg-muted rounded-md">
                <pre className="text-sm whitespace-pre-wrap font-mono" role="log" aria-label="Operation results">
                  {output}
                </pre>
              </div>
            )}
            
            {error && (
              <Alert variant="destructive" role="alert">
                <AlertCircle className="h-4 w-4" aria-hidden="true" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}