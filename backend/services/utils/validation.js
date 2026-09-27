const POSTCODE_REGEX = /^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$/i;

export const validatePostcode = (postcode) => {
  if (!postcode || typeof postcode !== 'string') {
    return { valid: false, error: 'Postcode required' };
  }

  const cleaned = postcode.trim().toUpperCase();
  
  if (!POSTCODE_REGEX.test(cleaned)) {
    return { valid: false, error: 'Invalid UK postcode format' };
  }

  return { valid: true, postcode: cleaned };
};