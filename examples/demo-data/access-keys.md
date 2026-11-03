# Rotating object storage access keys

Create a new read-only access key for the retrieval service. Update the service's secret configuration and restart it. Run a sync to verify ListBucket and GetObject permissions. Revoke the previous key only after the verification succeeds.

Use IAM roles instead of long-lived keys where your provider supports them. Never place production credentials in an agent prompt or a repository.
