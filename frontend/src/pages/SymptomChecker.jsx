import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { symptomCheckerApi } from '@/api';

export default function SymptomChecker() {
  const [formData, setFormData] = useState({
    age: '',
    gender: 'male',
    occupation: '',
    nationality: '',
    weight: '',
    chronic_diseases: '',
    allergies: '',
    previous_surgeries: '',
    current_medications: '',
    smoking_status: '',
    alcohol_intake: '',
    occasional_drug_use: '',
    symptoms: '',
  });
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult('');

    try {
      const payload = {
        ...formData,
        existing_medical_symptoms: formData.symptoms.split(',').map(s => s.trim()),
      };

      const data = await symptomCheckerApi.checkSymptoms(payload);

      setResult(data.result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit form');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="max-w-3xl mx-auto">
        <CardHeader>
          <CardTitle className="text-2xl font-bold text-gray-900">Symptom Checker</CardTitle>
        </CardHeader>
        
        <form onSubmit={handleSubmit}>
          <CardContent className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {/* Personal Information */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  name="age"
                  type="number"
                  value={formData.age}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <Label htmlFor="gender">Gender</Label>
                <Select
                  name="gender"
                  value={formData.gender}
                  onValueChange={(value) => setFormData({...formData, gender: value})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="male">Male</SelectItem>
                    <SelectItem value="female">Female</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="occupation">Occupation</Label>
                <Input
                  id="occupation"
                  name="occupation"
                  value={formData.occupation}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <Label htmlFor="nationality">Nationality</Label>
                <Input
                  id="nationality"
                  name="nationality"
                  value={formData.nationality}
                  onChange={handleChange}
                  required
                />
              </div>

              <div>
                <Label htmlFor="weight">Weight (kg)</Label>
                <Input
                  id="weight"
                  name="weight"
                  type="number"
                  value={formData.weight}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>

            {/* Medical History */}
            <div className="space-y-4">
              <div>
                <Label htmlFor="chronic_diseases">Chronic Diseases</Label>
                <Input
                  id="chronic_diseases"
                  name="chronic_diseases"
                  value={formData.chronic_diseases}
                  onChange={handleChange}
                />
              </div>

              <div>
                <Label htmlFor="allergies">Allergies</Label>
                <Input
                  id="allergies"
                  name="allergies"
                  value={formData.allergies}
                  onChange={handleChange}
                />
              </div>

              <div>
                <Label htmlFor="previous_surgeries">Previous Surgeries</Label>
                <Input
                  id="previous_surgeries"
                  name="previous_surgeries"
                  value={formData.previous_surgeries}
                  onChange={handleChange}
                />
              </div>

              <div>
                <Label htmlFor="current_medications">Current Medications</Label>
                <Input
                  id="current_medications"
                  name="current_medications"
                  value={formData.current_medications}
                  onChange={handleChange}
                />
              </div>

              <div>
                <Label htmlFor="smoking_status">Smoking Status</Label>
                <Input
                  id="smoking_status"
                  name="smoking_status"
                  value={formData.smoking_status}
                  onChange={handleChange}
                />
              </div>

              <div>
                <Label htmlFor="alcohol_intake">Alcohol Intake</Label>
                <Input
                  id="alcohol_intake"
                  name="alcohol_intake"
                  value={formData.alcohol_intake}
                  onChange={handleChange}
                />
              </div>

              <div>
                <Label htmlFor="occasional_drug_use">Occasional Drug Use</Label>
                <Input
                  id="occasional_drug_use"
                  name="occasional_drug_use"
                  value={formData.occasional_drug_use}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Symptoms */}
            <div className="md:col-span-2">
              <Label htmlFor="symptoms">Symptoms (comma separated)</Label>
              <Input
                id="symptoms"
                name="symptoms"
                value={formData.symptoms}
                onChange={handleChange}
                required
                className="mt-1"
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col gap-4">
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Analyzing...' : 'Check Symptoms'}
            </Button>

            {(result || error) && (
              <Alert variant={error ? "destructive" : "default"} className="w-full">
                <AlertDescription>
                  {error || result}
                </AlertDescription>
              </Alert>
            )}
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}