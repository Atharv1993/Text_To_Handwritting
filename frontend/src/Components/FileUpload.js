import React, { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [fname, setFname] = useState("");
  const [file, setFile] = useState(null);
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setImage(null);

    let title=file.name.split(".");
    setFname(`${title[0]}_handwritten.png`);

    if (!file) {
      setError("Please select a file to upload.");
      setLoading(false);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData,
        {
          responseType: "blob", // Ensures the response is treated as a file
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      // Create an object URL for the returned image
      const imageURL = URL.createObjectURL(response.data);
      setImage(imageURL);
    } catch (err) {
      setError("Failed to upload file. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (image) {
      const link = document.createElement("a");
      link.href = image;
      link.setAttribute("download", fname); // File name
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
    
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Upload a Document</h1>
      <form onSubmit={handleUpload} style={styles.form}>
        <input
          type="file"
          onChange={handleFileChange}
          accept=".txt,.pdf,.doc,.docx"
          style={styles.fileInput}
        />
        <button type="submit" disabled={loading} style={styles.uploadButton}>
          {loading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {error && <p style={styles.error}>{error}</p>}
      {image && (
        <div style={styles.imageContainer}>
          <h2 style={styles.imageTitle}>
            Generated Handwriting
            <button onClick={handleDownload} style={styles.downloadButton}>
              Download
            </button>
          </h2>
          <img
            src={image}
            alt="Handwritten Output"
            style={styles.image}
          />
        </div>
      )}
    </div>
  );

  
};

const styles = {
  container: {
    maxWidth: "600px",
    margin: "20px auto",
    padding: "20px",
    textAlign: "center",
    backgroundColor: "#f7f9fc",
    borderRadius: "10px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
  },
  title: {
    fontSize: "1.8rem",
    color: "#333",
    marginBottom: "20px",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  fileInput: {
    padding: "10px",
    margin: "10px 0",
    fontSize: "1rem",
    border: "1px solid #ccc",
    borderRadius: "5px",
    width: "100%",
    maxWidth: "300px",
  },
  uploadButton: {
    backgroundColor: "#4caf50",
    color: "white",
    padding: "10px 20px",
    fontSize: "1rem",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    transition: "background-color 0.3s",
  },
  uploadButtonHover: {
    backgroundColor: "#45a049",
  },
  error: {
    color: "#e74c3c",
    marginTop: "10px",
  },
  imageContainer: {
    marginTop: "20px",
    marginBottom: "20px",
    textAlign: "center",
  },
  imageTitle: {
    fontSize: "1.5rem",
    color: "#333",
    marginBottom: "10px",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
  },
  downloadButton: {
    backgroundColor: "#3498db",
    color: "white",
    padding: "5px 10px",
    fontSize: "0.9rem",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
    marginLeft: "10px",
    transition: "background-color 0.3s",
  },
  image: {
    width: "100%",
    maxWidth: "500px",
    border: "1px solid #ccc",
    borderRadius: "10px",
    boxShadow: "0 4px 6px rgba(0, 0, 0, 0.1)",
  },
};

export default FileUpload;
