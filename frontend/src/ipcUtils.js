export const formatPunishment = (punishment) => {
  if (!punishment || typeof punishment !== 'object') return 'Not specified';

  const parts = [];
  if (punishment.imprisonment && punishment.imprisonment !== 'not_applicable') {
    parts.push(`Imprisonment: ${punishment.imprisonment}`);
  }
  if (punishment.fine && punishment.fine !== 'not_applicable') {
    parts.push(`Fine: ${punishment.fine}`);
  }
  if (punishment.cognizable && punishment.cognizable !== 'not_applicable') {
    parts.push(`Cognizable: ${punishment.cognizable}`);
  }
  if (punishment.bailable && punishment.bailable !== 'not_applicable') {
    parts.push(`Bailable: ${punishment.bailable}`);
  }
  if (punishment.triable_by && punishment.triable_by !== 'not_applicable') {
    parts.push(`Triable by: ${punishment.triable_by}`);
  }

  return parts.length > 0 ? parts.join(', ') : 'Not applicable';
};

export const formatCitation = (citation) => {
  if (typeof citation === 'string') return citation;
  if (!citation || typeof citation !== 'object') return 'Indian Penal Code';

  const law = citation.law || 'Indian Penal Code';
  const section = citation.section ? `, Section ${citation.section}` : '';
  const verified = citation.verified ? ' (Verified)' : '';
  return `${law}${section}${verified}`;
};

export const normalizeList = (value) => (Array.isArray(value) ? value.filter(Boolean) : []);
