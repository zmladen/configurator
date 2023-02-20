import React, { useState } from "react";
import styles from "./Styles/DragAndDrop.module.css";

function DragAndDrop() {
  const [dragging, setDragging] = useState(false);

  const handleDragOver = (event) => {
    event.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    setDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);

    const files = Array.from(event.dataTransfer.files);
    // Handle dropped files
  };

  return (
    // <div className={`drop-zone${dragging ? " dragging" : ""}`} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
    <div className={dragging ? styles.dropZone : styles.dropZone} onDragOver={handleDragOver} onDragLeave={handleDragLeave} onDrop={handleDrop}>
      <p>Drag and drop files here</p>
    </div>
  );
}

export default DragAndDrop;
