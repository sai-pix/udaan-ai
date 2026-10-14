// Udaan AI Client Utilities

document.addEventListener('DOMContentLoaded', function () {
  // 1. Copy to clipboard utility
  window.copyToClipboard = function (text, btnElement) {
    if (!navigator.clipboard) {
      alert('Copied: ' + text);
      return;
    }
    navigator.clipboard.writeText(text).then(function () {
      if (btnElement) {
        const originalHtml = btnElement.innerHTML;
        btnElement.innerHTML = '<i class="bi bi-check-lg"></i> Copied!';
        btnElement.classList.add('btn-success');
        setTimeout(() => {
          btnElement.innerHTML = originalHtml;
          btnElement.classList.remove('btn-success');
        }, 2000);
      }
    }).catch(function (err) {
      console.error('Failed to copy: ', err);
    });
  };

  // 2. AI Profile Analyzer in Intake Form
  const analyzeBtn = document.getElementById('btn-analyze-ai');
  const naturalInput = document.getElementById('raw_natural_input');
  const aiStatusBox = document.getElementById('ai-status-box');

  if (analyzeBtn && naturalInput) {
    analyzeBtn.addEventListener('click', function () {
      const text = naturalInput.value.trim();
      if (text.length < 5) {
        alert('Please write at least a few words describing your experience or needs.');
        return;
      }

      analyzeBtn.disabled = true;
      const originalText = analyzeBtn.innerHTML;
      analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span> Analyzing text...';

      if (aiStatusBox) {
        aiStatusBox.innerHTML = '<div class="alert alert-info py-2 small mb-3"><i class="bi bi-cpu me-2"></i> Analyzing your words to identify skills, barriers, and support needs...</div>';
      }

      fetch('/intake/analyze-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: text,
          language: document.getElementById('preferred_language')?.value || 'en'
        })
      })
      .then(res => res.json())
      .then(data => {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = originalText;

        if (data.error) {
          if (aiStatusBox) {
            aiStatusBox.innerHTML = `<div class="alert alert-warning py-2 small mb-3">${data.error}</div>`;
          }
          return;
        }

        // Auto-fill skills
        const skillsField = document.getElementById('skills_input');
        if (skillsField && data.skills && data.skills.length > 0) {
          skillsField.value = data.skills.join(', ');
        }

        // Auto-check practical barriers
        if (data.practical_barriers && Array.isArray(data.practical_barriers)) {
          data.practical_barriers.forEach(barrierId => {
            const cb = document.querySelector(`input[name="practical_barriers"][value="${barrierId}"]`);
            if (cb) cb.checked = true;
          });
        }

        // Auto-check requested support
        if (data.support_needs && Array.isArray(data.support_needs)) {
          data.support_needs.forEach(catId => {
            const cb = document.querySelector(`input[name="requested_support"][value="${catId}"]`);
            if (cb) cb.checked = true;
          });
        }

        // Store structured JSON in hidden field
        const hiddenData = document.getElementById('structured_data_json');
        if (hiddenData) {
          hiddenData.value = JSON.stringify(data);
        }

        const hiddenAi = document.getElementById('ai_assisted');
        if (hiddenAi) {
          hiddenAi.value = data.ai_assisted ? 'true' : 'false';
        }

        // Show feedback status
        if (aiStatusBox) {
          const methodLabel = data.ai_assisted ? `Gemini AI (${data.extraction_method})` : `Rule Engine (${data.extraction_method})`;
          const badgeClass = data.ai_assisted ? 'badge bg-success' : 'badge bg-secondary';
          aiStatusBox.innerHTML = `
            <div class="alert alert-success py-2 small mb-3">
              <div class="d-flex justify-content-between align-items-center">
                <strong><i class="bi bi-check-circle-fill me-1"></i> Profile Extracted Successfully</strong>
                <span class="${badgeClass}">${methodLabel}</span>
              </div>
              <p class="mb-0 mt-1">${data.summary || 'Identified key skills and practical constraints.'}</p>
              ${data.notice ? `<small class="text-muted d-block mt-1">${data.notice}</small>` : ''}
            </div>
          `;
        }
      })
      .catch(err => {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = originalText;
        if (aiStatusBox) {
          aiStatusBox.innerHTML = `<div class="alert alert-danger py-2 small mb-3">Could not process text: ${err.message}</div>`;
        }
      });
    });
  }

  // 3. Pathway step status toggle via async API
  window.togglePathwayStep = function (stepId, newStatus, cardElement) {
    fetch(`/api/step/${stepId}/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.reload();
      }
    })
    .catch(err => {
      console.error(err);
      window.location.reload();
    });
  };
});
