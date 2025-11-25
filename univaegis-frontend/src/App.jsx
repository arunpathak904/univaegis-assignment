import React, { useState } from "react";
import {
  Container,
  Box,
  Typography,
  Button,
  TextField,
  MenuItem,
  Card,
  CardContent,
  Divider,
  CircularProgress,
  Alert,
  Grid,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import CancelIcon from "@mui/icons-material/Cancel";
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

function App() {
  // Upload state
  const [file, setFile] = useState(null);
  const [docType, setDocType] = useState("academic");
  const [uploading, setUploading] = useState(false);

  // Data from backend
  const [documentData, setDocumentData] = useState(null); // whole "document" object
  const [extractedData, setExtractedData] = useState(null); // "extracted" from backend
  const [uploadError, setUploadError] = useState("");

  // Editing extracted data
  const [editingFields, setEditingFields] = useState(false);
  const [editFormData, setEditFormData] = useState({});
  const [saveFieldsLoading, setSaveFieldsLoading] = useState(false);
  const [saveFieldsError, setSaveFieldsError] = useState("");
  const [saveFieldsSuccess, setSaveFieldsSuccess] = useState("");

  // IELTS & eligibility
  const [ieltsScores, setIeltsScores] = useState({
    listening: 8.0,
    reading: 8.0,
    writing: 8.0,
    speaking: 8.0,
  });
  const [checkingEligibility, setCheckingEligibility] = useState(false);
  const [eligibilityResult, setEligibilityResult] = useState(null);
  const [eligibilityError, setEligibilityError] = useState("");

  // Handlers
  const handleFileChange = (event) => {
    setFile(event.target.files[0] || null);
    // Clear previous data when new file selected
    setDocumentData(null);
    setExtractedData(null);
    setEligibilityResult(null);
    setUploadError("");
  };

  const handleDocTypeChange = (event) => {
    setDocType(event.target.value);
  };

    const handleUpload = async () => {
    if (!file) {
      setUploadError("Please choose a file to upload.");
      return;
    }

    setUploading(true);
    setUploadError("");
    setEligibilityResult(null);
    setSaveFieldsError("");
    setSaveFieldsSuccess("");
    setEditingFields(false);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", docType);

      const response = await axios.post(
        `${API_BASE_URL}/documents/upload/`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      const data = response.data;
      if (data.success) {
        setDocumentData(data.document);
        const extracted = data.extracted || data.document.extracted_data || null;
        setExtractedData(extracted);

        // Initialize edit form data from extracted data
        if (extracted) {
          setEditFormData(extracted);
        } else {
          setEditFormData({});
        }

        // Reset editing state and messages
        setEditingFields(false);
        setSaveFieldsError("");
        setSaveFieldsSuccess("");
      } else {
        setUploadError("Upload failed. Please check input and try again.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      if (error.response && error.response.data) {
        setUploadError(
          `Upload failed: ${JSON.stringify(error.response.data)}`
        );
      } else {
        setUploadError("Upload failed due to a network or server error.");
      }
    } finally {
      setUploading(false);
    }
  };

  const handleIeltsChange = (field, value) => {
    setIeltsScores((prev) => ({
      ...prev,
      [field]: value === "" ? "" : parseFloat(value),
    }));
  };

  const handleCheckEligibility = async () => {
    if (!documentData || !documentData.id) {
      setEligibilityError("Please upload an academic document first.");
      return;
    }

    if (documentData.doc_type !== "academic") {
      setEligibilityError(
        "Eligibility check is only applicable to academic documents."
      );
      return;
    }

    setCheckingEligibility(true);
    setEligibilityError("");
    setEligibilityResult(null);

    try {
      const payload = {
        document_id: documentData.id,
        ielts_scores: {
          listening: Number(ieltsScores.listening),
          reading: Number(ieltsScores.reading),
          writing: Number(ieltsScores.writing),
          speaking: Number(ieltsScores.speaking),
        },
      };

      const response = await axios.post(
        `${API_BASE_URL}/eligibility/check/`,
        payload
      );

      setEligibilityResult(response.data);
    } catch (error) {
      console.error("Eligibility error:", error);
      if (error.response && error.response.data) {
        setEligibilityError(
          `Eligibility check failed: ${JSON.stringify(error.response.data)}`
        );
      } else {
        setEligibilityError("Eligibility check failed due to a network or server error.");
      }
    } finally {
      setCheckingEligibility(false);
    }
  };

  const handleStartEditing = () => {
    if (extractedData) {
      setEditFormData(extractedData);
      setEditingFields(true);
      setSaveFieldsError("");
      setSaveFieldsSuccess("");
    }
  };

  const handleEditFieldChange = (field, value) => {
    setEditFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleSaveEditedFields = async () => {
    if (!documentData || !documentData.id) {
      setSaveFieldsError("No document loaded to update.");
      return;
    }

    setSaveFieldsLoading(true);
    setSaveFieldsError("");
    setSaveFieldsSuccess("");

    try {
      // Build payload: only send relevant fields (for academic doc)
      const payload = {};

      if (documentData.doc_type === "academic") {
        const possibleFields = [
          "student_name",
          "university",
          "course",
          "percentage",
          "gpa",
          "year_of_passing",
        ];
        possibleFields.forEach((field) => {
          if (field in editFormData) {
            // Convert types for numeric fields
            if (field === "percentage" || field === "gpa") {
              const num = editFormData[field];
              payload[field] = num === "" || num === null ? null : Number(num);
            } else if (field === "year_of_passing") {
              const num = editFormData[field];
              payload[field] = num === "" || num === null ? null : Number(num);
            } else {
              payload[field] = editFormData[field];
            }
          }
        });
      } else if (documentData.doc_type === "financial") {
        const possibleFields = [
          "bank_name",
          "account_holder",
          "available_balance",
          "date",
        ];
        possibleFields.forEach((field) => {
          if (field in editFormData) {
            if (field === "available_balance") {
              const num = editFormData[field];
              payload[field] = num === "" || num === null ? null : Number(num);
            } else {
              payload[field] = editFormData[field];
            }
          }
        });
      }

      const response = await axios.patch(
        `${API_BASE_URL}/documents/${documentData.id}/update-extracted/`,
        payload
      );

      const data = response.data;
      if (data.success) {
        setDocumentData(data.document);
        setExtractedData(data.document.extracted_data);
        setEditFormData(data.document.extracted_data || {});
        setEditingFields(false);
        setSaveFieldsSuccess("Fields updated successfully.");
      } else {
        setSaveFieldsError("Failed to update fields.");
      }
    } catch (error) {
      console.error("Save fields error:", error);
      if (error.response && error.response.data) {
        setSaveFieldsError(
          `Save failed: ${JSON.stringify(error.response.data)}`
        );
      } else {
        setSaveFieldsError("Save failed due to a network or server error.");
      }
    } finally {
      setSaveFieldsLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        UnivAegis – Document Verification & Eligibility
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Upload academic or financial documents, extract key data using OCR, and
        check eligibility based on academic performance and IELTS scores.
      </Typography>

      {/* Upload Section */}
      <Card sx={{ mt: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            1. Upload Document
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <Button
                component="label"
                variant="outlined"
                startIcon={<CloudUploadIcon />}
                fullWidth
              >
                {file ? file.name : "Choose File"}
                <input
                  type="file"
                  hidden
                  onChange={handleFileChange}
                  accept=".pdf,.jpg,.jpeg,.png"
                />
              </Button>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                select
                label="Document Type"
                value={docType}
                onChange={handleDocTypeChange}
                fullWidth
                size="small"
              >
                <MenuItem value="academic">Academic</MenuItem>
                <MenuItem value="financial">Financial</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <Button
                variant="contained"
                onClick={handleUpload}
                fullWidth
                disabled={uploading}
              >
                {uploading ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} /> Uploading...
                  </>
                ) : (
                  "Upload & Extract"
                )}
              </Button>
            </Grid>
          </Grid>

          {uploadError && (
            <Box mt={2}>
              <Alert severity="error">{uploadError}</Alert>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Extracted Data */}
      {documentData && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              2. Extracted Document Data
            </Typography>

            <Typography variant="body2" color="text.secondary">
              <strong>Document ID:</strong> {documentData.id} &nbsp;|&nbsp;
              <strong>Type:</strong> {documentData.doc_type} &nbsp;|&nbsp;
              <strong>File:</strong> {documentData.original_filename}
            </Typography>

            <Divider sx={{ my: 2 }} />

            {extractedData ? (
              <Box>
                <Typography variant="subtitle1" gutterBottom>
                  Extracted Fields
                </Typography>

                {/* Editable form for academic documents */}
                {documentData.doc_type === "academic" && (
                  <Box>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          label="Student Name"
                          value={editFormData.student_name || ""}
                          onChange={(e) =>
                            handleEditFieldChange("student_name", e.target.value)
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          label="University / School"
                          value={editFormData.university || ""}
                          onChange={(e) =>
                            handleEditFieldChange("university", e.target.value)
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          label="Course Name"
                          value={editFormData.course || ""}
                          onChange={(e) =>
                            handleEditFieldChange("course", e.target.value)
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={3}>
                        <TextField
                          label="Percentage"
                          type="number"
                          inputProps={{ step: "0.1", min: "0", max: "100" }}
                          value={
                            editFormData.percentage === null ||
                            editFormData.percentage === undefined
                              ? ""
                              : editFormData.percentage
                          }
                          onChange={(e) =>
                            handleEditFieldChange("percentage", e.target.value)
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={3}>
                        <TextField
                          label="GPA"
                          type="number"
                          inputProps={{ step: "0.1", min: "0", max: "10" }}
                          value={
                            editFormData.gpa === null ||
                            editFormData.gpa === undefined
                              ? ""
                              : editFormData.gpa
                          }
                          onChange={(e) =>
                            handleEditFieldChange("gpa", e.target.value)
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={3}>
                        <TextField
                          label="Year of Passing"
                          type="number"
                          inputProps={{ min: "1900", max: "2100" }}
                          value={
                            editFormData.year_of_passing === null ||
                            editFormData.year_of_passing === undefined
                              ? ""
                              : editFormData.year_of_passing
                          }
                          onChange={(e) =>
                            handleEditFieldChange(
                              "year_of_passing",
                              e.target.value
                            )
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                    </Grid>
                  </Box>
                )}

                {/* Editable form for financial documents */}
                {documentData.doc_type === "financial" && (
                  <Box>
                    <Grid container spacing={2}>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          label="Bank Name"
                          value={editFormData.bank_name || ""}
                          onChange={(e) =>
                            handleEditFieldChange("bank_name", e.target.value)
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={6}>
                        <TextField
                          label="Account Holder"
                          value={editFormData.account_holder || ""}
                          onChange={(e) =>
                            handleEditFieldChange(
                              "account_holder",
                              e.target.value
                            )
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <TextField
                          label="Available Balance"
                          type="number"
                          inputProps={{ step: "0.01", min: "0" }}
                          value={
                            editFormData.available_balance === null ||
                            editFormData.available_balance === undefined
                              ? ""
                              : editFormData.available_balance
                          }
                          onChange={(e) =>
                            handleEditFieldChange(
                              "available_balance",
                              e.target.value
                            )
                          }
                          fullWidth
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <TextField
                          label="Date"
                          value={editFormData.date || ""}
                          onChange={(e) =>
                            handleEditFieldChange("date", e.target.value)
                          }
                          fullWidth
                          size="small"
                          helperText="e.g., 01-04-2024 or 2024-04-01"
                        />
                      </Grid>
                    </Grid>
                  </Box>
                )}

                {/* Save button + messages */}
                <Box mt={2}>
                  <Button
                    variant="outlined"
                    onClick={handleSaveEditedFields}
                    disabled={saveFieldsLoading}
                  >
                    {saveFieldsLoading ? (
                      <>
                        <CircularProgress size={20} sx={{ mr: 1 }} /> Saving...
                      </>
                    ) : (
                      "Save Corrected Fields"
                    )}
                  </Button>
                </Box>

                {saveFieldsError && (
                  <Box mt={1}>
                    <Alert severity="error">{saveFieldsError}</Alert>
                  </Box>
                )}
                {saveFieldsSuccess && (
                  <Box mt={1}>
                    <Alert severity="success">{saveFieldsSuccess}</Alert>
                  </Box>
                )}

                {/* Raw JSON preview */}
                <Typography variant="subtitle2" sx={{ mt: 3 }}>
                  Raw Extracted JSON (after save)
                </Typography>
                <Box
                  component="pre"
                  sx={{
                    backgroundColor: "#f5f5f5",
                    p: 2,
                    borderRadius: 2,
                    maxHeight: 250,
                    overflow: "auto",
                    fontSize: 13,
                  }}
                >
                  {JSON.stringify(extractedData, null, 2)}
                </Box>
              </Box>
            ) : (
              <Alert severity="warning" sx={{ mt: 2 }}>
                No extracted data found for this document.
              </Alert>
            )}

          </CardContent>
        </Card>
      )}

      {/* Eligibility Section – only for academic docs */}
      {documentData && documentData.doc_type === "academic" && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              3. IELTS Scores & Eligibility
            </Typography>

            <Typography variant="body2" color="text.secondary" gutterBottom>
              Enter IELTS band scores (minimum 8.0 required in each band).
            </Typography>

            <Grid container spacing={2} sx={{ mt: 1 }}>
              {["listening", "reading", "writing", "speaking"].map((field) => (
                <Grid item xs={12} sm={3} key={field}>
                  <TextField
                    label={field.charAt(0).toUpperCase() + field.slice(1)}
                    type="number"
                    inputProps={{ step: "0.5", min: "0", max: "9" }}
                    value={ieltsScores[field]}
                    onChange={(e) => handleIeltsChange(field, e.target.value)}
                    fullWidth
                    size="small"
                  />
                </Grid>
              ))}
            </Grid>

            <Box mt={2}>
              <Button
                variant="contained"
                onClick={handleCheckEligibility}
                disabled={checkingEligibility}
              >
                {checkingEligibility ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} /> Checking...
                  </>
                ) : (
                  "Check Eligibility"
                )}
              </Button>
            </Box>

            {eligibilityError && (
              <Box mt={2}>
                <Alert severity="error">{eligibilityError}</Alert>
              </Box>
            )}

            {eligibilityResult && (
              <Box mt={3}>
                <Typography variant="subtitle1" gutterBottom>
                  Eligibility Result
                </Typography>
                <Card
                  sx={{
                    backgroundColor: eligibilityResult.eligible
                      ? "#e8f5e9"
                      : "#ffebee",
                  }}
                >
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={1}>
                      {eligibilityResult.eligible ? (
                        <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                      ) : (
                        <CancelIcon color="error" sx={{ mr: 1 }} />
                      )}
                      <Typography variant="h6">
                        {eligibilityResult.eligible ? "Eligible" : "Not Eligible"}
                      </Typography>
                    </Box>
                    {eligibilityResult.reasons &&
                    eligibilityResult.reasons.length > 0 ? (
                      <Box component="ul" sx={{ pl: 3, mb: 0 }}>
                        {eligibilityResult.reasons.map((reason, idx) => (
                          <li key={idx}>
                            <Typography variant="body2">{reason}</Typography>
                          </li>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2">
                        No issues found. All criteria satisfied.
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Box>
            )}
          </CardContent>
        </Card>
      )}
    </Container>
  );
}

export default App;
