import { useRef, useState } from "react";
import { getPresignedUrl, triggerProcessing } from "../api";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { CheckCircle2, UploadCloud, XCircle } from "lucide-react";

// Each item: { name, progress (0-100), status: "pending"|"uploading"|"done"|"error" }
function initFileState(files) {
  return files.map((f) => ({ name: f.name, progress: 0, status: "pending" }));
}

function ProgressBar({ percent }) {
  return (
    <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
      <div
        className="h-full rounded-full bg-cyan-500 transition-all duration-300"
        style={{ width: `${percent}%` }}
      />
    </div>
  );
}

function UploadCard({ onProcessingStarted }) {
  const [files, setFiles] = useState([]);
  const [fileStates, setFileStates] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  const updateFileState = (index, patch) => {
    setFileStates((prev) =>
      prev.map((f, i) => (i === index ? { ...f, ...patch } : f))
    );
  };

  const handleUpload = async () => {
    if (!files.length) return;

    setUploading(true);
    setFileStates(initFileState(files));

    const uploadedFiles = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];

      try {
        // 1. Get presigned S3 URL
        const presignedRes = await getPresignedUrl(file.name);
        const { url, key } = presignedRes.data;

        updateFileState(i, { status: "uploading" });

        // 2. PUT directly to S3 via XHR.
        // Using XHR instead of axios so the browser sets Content-Type from the
        // File object itself — axios would inject its own default header which
        // corrupts the binary body and triggers unexpected CORS preflight.
        await new Promise((resolve, reject) => {
          const xhr = new XMLHttpRequest();
          xhr.open("PUT", url);
          xhr.upload.onprogress = (evt) => {
            const pct = evt.total ? Math.round((evt.loaded * 100) / evt.total) : 0;
            updateFileState(i, { progress: pct });
          };
          xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
              resolve();
            } else {
              reject(new Error(`S3 upload failed: ${xhr.status} ${xhr.responseText}`));
            }
          };
          xhr.onerror = () => reject(new Error("Network error during S3 upload"));
          xhr.send(file);
        });

        updateFileState(i, { progress: 100, status: "done" });
        toast.success(`${file.name} uploaded to S3`, { duration: 3000 });
        uploadedFiles.push({ filename: file.name, s3_key: key });
      } catch (err) {
        console.error(`Upload failed for ${file.name}:`, err);
        updateFileState(i, { status: "error" });
        toast.error(`Failed to upload ${file.name}`, { duration: 3000 });
      }
    }

    // 3. Trigger backend processing for all successfully uploaded files
    if (uploadedFiles.length > 0) {
      try {
        const processRes = await triggerProcessing(uploadedFiles);
        const jobs = processRes.data.jobs;
        if (onProcessingStarted) onProcessingStarted(jobs);
        toast.info(
          `${jobs.length} file${jobs.length > 1 ? "s" : ""} sent for processing`,
          { description: "Check the Processing Status section below.", duration: 3000 }
        );
      } catch (err) {
        console.error("Failed to trigger processing:", err);
        toast.error("Failed to start processing. Check backend status.", { duration: 3000 });
      }
    }

    setFiles([]);
    if (fileInputRef.current) fileInputRef.current.value = "";
    setUploading(false);
  };

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files || []));
    setFileStates([]);
  };

  return (
    <Card className="enterprise-card">
      <CardHeader>
        <CardTitle>Upload Lease Documents</CardTitle>
        <CardDescription>
          Files are uploaded directly to S3, then processed in the background. Progress is shown per file.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input
          ref={fileInputRef}
          type="file"
          multiple
          className="cursor-pointer"
          disabled={uploading}
          onChange={handleFileChange}
        />

        {/* Pre-upload file list */}
        {files.length > 0 && fileStates.every((f) => f.status === "pending") && (
          <div className="rounded-md border bg-muted/40 p-3">
            <p className="text-sm font-medium">{files.length} file(s) selected</p>
            <ul className="mt-2 max-h-28 list-disc space-y-1 overflow-auto pl-5 text-xs text-muted-foreground">
              {files.map((file, idx) => (
                <li key={`${file.name}-${idx}`}>{file.name}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Per-file upload progress */}
        {fileStates.some((f) => f.status !== "pending") && (
          <div className="space-y-2">
            {fileStates.map((f, idx) => (
              <div key={idx} className="rounded-md border bg-white/70 px-3 py-2">
                <div className="flex items-center justify-between gap-2">
                  <span className="max-w-[260px] truncate text-xs font-medium text-slate-700">
                    {f.name}
                  </span>
                  <span className="flex shrink-0 items-center gap-1 text-xs text-muted-foreground">
                    {f.status === "done" && (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
                    )}
                    {f.status === "error" && (
                      <XCircle className="h-3.5 w-3.5 text-red-500" />
                    )}
                    {f.status === "uploading" && `${f.progress}%`}
                    {f.status === "done" && "Uploaded"}
                    {f.status === "error" && "Failed"}
                    {f.status === "pending" && "Waiting…"}
                  </span>
                </div>
                {(f.status === "uploading" || f.status === "done") && (
                  <div className="mt-1.5">
                    <ProgressBar percent={f.progress} />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <Button
          className="w-full md:w-auto gap-2"
          onClick={handleUpload}
          disabled={!files.length || uploading}
        >
          <UploadCloud className="h-4 w-4" />
          {uploading
            ? "Uploading to S3…"
            : `Upload ${files.length || ""} Document${files.length === 1 ? "" : "s"}`}
        </Button>
      </CardContent>
    </Card>
  );
}

export default UploadCard;
