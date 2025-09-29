import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { AlertCircle, Cpu, Thermometer, Zap, Activity, Settings, Shield } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface CPUInfo {
  model: string;
  cores: number;
  threads: number;
  frequency: {
    current: number;
    min: number;
    max: number;
  };
  governor: string;
  available_governors: string[];
  temperature: number | null;
  usage: number;
  load_average: number[];
}

interface StressTestResult {
  duration: number;
  initial_temperature: number | null;
  final_temperature: number | null;
  temperature_delta: number | null;
  success: boolean;
  output: string;
  error?: string;
}

export default function CPUManager() {
  const [selectedOption, setSelectedOption] = useState<string>("");
  const [governor, setGovernor] = useState<string>("");
  const [frequency, setFrequency] = useState<string>("");
  const [duration, setDuration] = useState<string>("60");
  const [output, setOutput] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [cpuInfo, setCpuInfo] = useState<CPUInfo | null>(null);
  const [stressTestResults, setStressTestResults] = useState<StressTestResult | null>(null);
  const [validationErrors, setValidationErrors] = useState<{[key: string]: string}>({});

  // Simulated API calls - replace with actual backend calls
  const fetchCPUInfo = async (): Promise<CPUInfo> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      model: "AMD Ryzen 7 5800X",
      cores: 8,
      threads: 16,
      frequency: {
        current: 3200.5,
        min: 800.0,
        max: 4700.0
      },
      governor: "performance",
      available_governors: ["performance", "powersave", "ondemand", "conservative", "schedutil"],
      temperature: 45.2,
      usage: 25.4,
      load_average: [1.2, 1.5, 1.8]
    };
  };

  const setCPUGovernor = async (gov: string): Promise<{success: boolean, error?: string}> => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return Math.random() > 0.1 ? {success: true} : {success: false, error: "Failed to set governor"};
  };

  const setCPUFrequency = async (freq: string): Promise<{success: boolean, error?: string}> => {
    await new Promise(resolve => setTimeout(resolve, 2000));
    return Math.random() > 0.1 ? {success: true} : {success: false, error: "Failed to set frequency"};
  };

  const runStressTest = async (dur: number): Promise<StressTestResult> => {
    await new Promise(resolve => setTimeout(resolve, dur * 100)); // Simulate test
    
    return {
      duration: dur,
      initial_temperature: 45.2,
      final_temperature: 78.5,
      temperature_delta: 33.3,
      success: true,
      output: `Stress test completed successfully for ${dur} seconds`
    };
  };

  // Input validation functions
  const validateGovernor = (value: string): string | null => {
    if (!value.trim()) return "Governor name is required";
    if (!/^[a-z_]+$/.test(value)) return "Invalid governor: must contain only lowercase letters and underscores";
    return null;
  };

  const validateFrequency = (value: string): string | null => {
    if (!value.trim()) return "Frequency value is required";
    if (!/^(\d+|min|max)$/.test(value)) return "Invalid frequency: must be a number, 'min', or 'max'";
    if (value.match(/^\d+$/)) {
      const freq = parseInt(value);
      if (freq < 100000 || freq > 10000000) return "Frequency must be between 100MHz and 10GHz";
    }
    return null;
  };

  const validateDuration = (value: string): string | null => {
    if (!value.trim()) return "Duration is required";
    if (!/^\d+$/.test(value)) return "Invalid duration: must be a positive integer";
    const dur = parseInt(value);
    if (dur < 1 || dur > 3600) return "Duration must be between 1 and 3600 seconds";
    return null;
  };

  // Load CPU info on component mount
  useEffect(() => {
    const loadCPUInfo = async () => {
      try {
        setLoading(true);
        const info = await fetchCPUInfo();
        setCpuInfo(info);
        setGovernor(info.governor);
      } catch (err) {
        setError("Failed to load CPU information");
      } finally {
        setLoading(false);
      }
    };

    loadCPUInfo();
  }, []);

  const handleOptionSelect = async (value: string) => {
    setSelectedOption(value);
    setOutput("");
    setError("");
    setValidationErrors({});

    if (value === "1" && cpuInfo) {
      setOutput(`CPU Model: ${cpuInfo.model}
Cores: ${cpuInfo.cores} physical, ${cpuInfo.threads} logical
Current Frequency: ${cpuInfo.frequency.current.toFixed(1)} MHz
Frequency Range: ${cpuInfo.frequency.min} - ${cpuInfo.frequency.max} MHz
Current Governor: ${cpuInfo.governor}
Temperature: ${cpuInfo.temperature ? cpuInfo.temperature.toFixed(1) + '°C' : 'N/A'}
CPU Usage: ${cpuInfo.usage.toFixed(1)}%
Load Average: ${cpuInfo.load_average.map(l => l.toFixed(2)).join(', ')}`);
    }
  };

  const handleGovernorSubmit = async () => {
    const validationError = validateGovernor(governor);
    if (validationError) {
      setValidationErrors({governor: validationError});
      return;
    }

    setLoading(true);
    setValidationErrors({});
    
    try {
      const result = await setCPUGovernor(governor);
      if (result.success) {
        setOutput(`Successfully set CPU governor to: ${governor}`);
        // Refresh CPU info
        const info = await fetchCPUInfo();
        setCpuInfo(info);
      } else {
        setError(result.error || "Failed to set governor");
      }
    } catch (err) {
      setError("An error occurred while setting the governor");
    } finally {
      setLoading(false);
    }
  };

  const handleFrequencySubmit = async () => {
    const validationError = validateFrequency(frequency);
    if (validationError) {
      setValidationErrors({frequency: validationError});
      return;
    }

    setLoading(true);
    setValidationErrors({});
    
    try {
      const result = await setCPUFrequency(frequency);
      if (result.success) {
        setOutput(`Successfully set CPU frequency to: ${frequency}${frequency.match(/^\d+$/) ? 'kHz' : ''}`);
        // Refresh CPU info
        const info = await fetchCPUInfo();
        setCpuInfo(info);
      } else {
        setError(result.error || "Failed to set frequency");
      }
    } catch (err) {
      setError("An error occurred while setting the frequency");
    } finally {
      setLoading(false);
    }
  };

  const handleStressTest = async () => {
    const validationError = validateDuration(duration);
    if (validationError) {
      setValidationErrors({duration: validationError});
      return;
    }

    setLoading(true);
    setValidationErrors({});
    
    try {
      const results = await runStressTest(parseInt(duration));
      setStressTestResults(results);
      setOutput(`Stress test completed successfully!
Duration: ${results.duration} seconds
Initial Temperature: ${results.initial_temperature?.toFixed(1)}°C
Final Temperature: ${results.final_temperature?.toFixed(1)}°C
Temperature Increase: ${results.temperature_delta?.toFixed(1)}°C`);
    } catch (err) {
      setError("An error occurred during the stress test");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2" role="heading" aria-level={1}>
            <Cpu className="h-6 w-6" aria-hidden="true" />
            CPU Management System
            <Shield className="h-5 w-5 text-green-600" aria-label="Secure system" />
          </CardTitle>
        </CardHeader>
      </Card>

      {/* CPU Information Overview */}
      {cpuInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" aria-hidden="true" />
              System Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-sm font-medium">CPU Model</Label>
                <p className="text-sm text-muted-foreground">{cpuInfo.model}</p>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium">Cores/Threads</Label>
                <p className="text-sm text-muted-foreground">{cpuInfo.cores}/{cpuInfo.threads}</p>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium">Current Governor</Label>
                <p className="text-sm text-muted-foreground">{cpuInfo.governor}</p>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium">Frequency</Label>
                <p className="text-sm text-muted-foreground">{cpuInfo.frequency.current.toFixed(1)} MHz</p>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium flex items-center gap-1">
                  <Thermometer className="h-4 w-4" aria-hidden="true" />
                  Temperature
                </Label>
                <p className="text-sm text-muted-foreground">
                  {cpuInfo.temperature ? `${cpuInfo.temperature.toFixed(1)}°C` : 'N/A'}
                </p>
              </div>
              
              <div className="space-y-2">
                <Label className="text-sm font-medium">CPU Usage</Label>
                <div className="space-y-1">
                  <Progress value={cpuInfo.usage} className="w-full" aria-label={`CPU usage: ${cpuInfo.usage.toFixed(1)}%`} />
                  <p className="text-xs text-muted-foreground">{cpuInfo.usage.toFixed(1)}%</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" aria-hidden="true" />
            CPU Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Operation Selection */}
          <div className="space-y-2">
            <Label htmlFor="operation-select">Select Operation</Label>
            <Select 
              onValueChange={handleOptionSelect} 
              value={selectedOption}
              disabled={loading}
            >
              <SelectTrigger id="operation-select" aria-label="Select CPU operation">
                <SelectValue placeholder="Choose a CPU management operation" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Show CPU Information</SelectItem>
                <SelectItem value="2">Set CPU Governor</SelectItem>
                <SelectItem value="3">Set CPU Frequency</SelectItem>
                <SelectItem value="4">Show Temperature</SelectItem>
                <SelectItem value="5">CPU Stress Test</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Separator />

          {/* Governor Control */}
          {selectedOption === "2" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="governor-input">CPU Governor</Label>
                <Input
                  id="governor-input"
                  placeholder="Enter governor (e.g., performance, powersave)"
                  value={governor}
                  onChange={(e) => setGovernor(e.target.value)}
                  disabled={loading}
                  aria-describedby={validationErrors.governor ? "governor-error" : "governor-help"}
                  aria-invalid={!!validationErrors.governor}
                />
                {validationErrors.governor && (
                  <p id="governor-error" className="text-sm text-destructive" role="alert">
                    {validationErrors.governor}
                  </p>
                )}
                {cpuInfo && (
                  <p id="governor-help" className="text-sm text-muted-foreground">
                    Available: {cpuInfo.available_governors.join(', ')}
                  </p>
                )}
              </div>
              <Button 
                onClick={handleGovernorSubmit} 
                disabled={loading || !governor.trim()}
                className="w-full md:w-auto"
                aria-label="Set CPU governor"
              >
                {loading ? "Setting Governor..." : "Set Governor"}
              </Button>
            </div>
          )}

          {/* Frequency Control */}
          {selectedOption === "3" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="frequency-input">CPU Frequency</Label>
                <Input
                  id="frequency-input"
                  placeholder="Enter frequency in kHz (or min/max)"
                  value={frequency}
                  onChange={(e) => setFrequency(e.target.value)}
                  disabled={loading}
                  aria-describedby={validationErrors.frequency ? "frequency-error" : "frequency-help"}
                  aria-invalid={!!validationErrors.frequency}
                />
                {validationErrors.frequency && (
                  <p id="frequency-error" className="text-sm text-destructive" role="alert">
                    {validationErrors.frequency}
                  </p>
                )}
                {cpuInfo && (
                  <p id="frequency-help" className="text-sm text-muted-foreground">
                    Range: {cpuInfo.frequency.min} - {cpuInfo.frequency.max} MHz
                  </p>
                )}
              </div>
              <Button 
                onClick={handleFrequencySubmit} 
                disabled={loading || !frequency.trim()}
                className="w-full md:w-auto"
                aria-label="Set CPU frequency"
              >
                {loading ? "Setting Frequency..." : "Set Frequency"}
              </Button>
            </div>
          )}

          {/* Temperature Display */}
          {selectedOption === "4" && cpuInfo && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Thermometer className="h-5 w-5" aria-hidden="true" />
                <span className="font-medium">Current Temperature</span>
              </div>
              <div className="text-2xl font-bold">
                {cpuInfo.temperature ? `${cpuInfo.temperature.toFixed(1)}°C` : 'Temperature sensor not available'}
              </div>
              {cpuInfo.temperature && (
                <Progress 
                  value={Math.min((cpuInfo.temperature / 100) * 100, 100)} 
                  className="w-full"
                  aria-label={`CPU temperature: ${cpuInfo.temperature.toFixed(1)}°C`}
                />
              )}
            </div>
          )}

          {/* Stress Test */}
          {selectedOption === "5" && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="duration-input">Test Duration (seconds)</Label>
                <Input
                  id="duration-input"
                  placeholder="Enter test duration (1-3600 seconds)"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  disabled={loading}
                  aria-describedby={validationErrors.duration ? "duration-error" : "duration-help"}
                  aria-invalid={!!validationErrors.duration}
                />
                {validationErrors.duration && (
                  <p id="duration-error" className="text-sm text-destructive" role="alert">
                    {validationErrors.duration}
                  </p>
                )}
                <p id="duration-help" className="text-sm text-muted-foreground">
                  Recommended: 60-300 seconds for safe testing
                </p>
              </div>
              
              <div className="flex items-center gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
                <AlertCircle className="h-4 w-4 text-yellow-600" aria-hidden="true" />
                <span className="text-sm text-yellow-800">
                  Warning: Stress testing will increase CPU temperature and power consumption
                </span>
              </div>
              
              <Button 
                onClick={handleStressTest} 
                disabled={loading || !duration.trim()}
                className="w-full md:w-auto"
                variant="outline"
                aria-label="Run CPU stress test"
              >
                <Zap className="h-4 w-4 mr-2" aria-hidden="true" />
                {loading ? "Running Test..." : "Run Stress Test"}
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

      {/* Stress Test Results */}
      {stressTestResults && (
        <Card>
          <CardHeader>
            <CardTitle>Stress Test Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Test Duration</Label>
                <p className="text-lg font-semibold">{stressTestResults.duration}s</p>
              </div>
              
              {stressTestResults.temperature_delta && (
                <div className="space-y-2">
                  <Label>Temperature Increase</Label>
                  <p className="text-lg font-semibold text-orange-600">
                    +{stressTestResults.temperature_delta.toFixed(1)}°C
                  </p>
                </div>
              )}
            </div>
            
            {stressTestResults.initial_temperature && stressTestResults.final_temperature && (
              <div className="space-y-2">
                <Label>Temperature Profile</Label>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Initial: {stressTestResults.initial_temperature.toFixed(1)}°C</span>
                    <span>Final: {stressTestResults.final_temperature.toFixed(1)}°C</span>
                  </div>
                  <Progress 
                    value={(stressTestResults.final_temperature / 100) * 100} 
                    className="w-full"
                    aria-label={`Final temperature: ${stressTestResults.final_temperature.toFixed(1)}°C`}
                  />
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}