import { useState } from 'react';
import { Upload, X, Link, Sparkles } from 'lucide-react';
import "./fileupload.css"

export default function FileUpload({ title = "Upload Files" }) {
  const [files, setFiles] = useState([]);
  const [urlInput, setUrlInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles([...files, ...newFiles]);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const newFiles = Array.from(e.dataTransfer.files);
    setFiles([...files, ...newFiles]);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const removeFile = (index) => {
    setFiles(files.filter((_, i) => i !== index));
  };

  const handleProcess = () => {
    console.log('Processing files:', files);
    console.log('URL:', urlInput);
  };

  return (
    <div className="upload-container">
      <div className="upload-header">
        <h2>{title}</h2>
        <div className="file-counter">
          <span className="counter-badge">{files.length}</span>
        </div>
      </div>

      <label 
        className={`upload-area ${isDragging ? 'dragging' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <div className="upload-icon">
          <Upload size={40} strokeWidth={1.5} />
        </div>
        <p className="upload-title">Drop files here or click to browse</p>
        <p className="upload-subtitle">PNG, JPG, PDF, MP4 • Max 50MB</p>
        <input 
          type="file" 
          multiple 
          onChange={handleFileChange}
        />
      </label>

      {files.length > 0 && (
        <div className="file-list">
          {files.map((file, index) => (
            <div key={index} className="file-item">
              <div className="file-info">
                <span className="file-name">{file.name}</span>
                <span className="file-size">
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>
              <button 
                className="file-remove"
                onClick={() => removeFile(index)}
              >
                <X size={18} />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="url-section">
        <div className="url-icon">
          <Link size={18} />
        </div>
        <input
          type="text"
          className="url-input"
          placeholder="Paste URL of file on web..."
          value={urlInput}
          onChange={(e) => setUrlInput(e.target.value)}
        />
      </div>

      <button 
        className="process-btn"
        onClick={handleProcess}
        disabled={files.length === 0 && !urlInput}
      >
        <Sparkles size={18} />
        <span>Start Processing</span>
      </button>
    </div>
  );
}