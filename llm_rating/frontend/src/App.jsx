import { useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [review, setReview] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!review.trim()) return

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(`${API_URL}/api/predict/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ review: review.trim() }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Erreur serveur')
      }

      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const renderStars = (rating) => {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating)
  }

  return (
    <div className="container">
      <h1>Prédiction de Note</h1>
      <p className="subtitle">Entrez un avis client et Claude prédit sa note</p>

      <form onSubmit={handleSubmit}>
        <textarea
          value={review}
          onChange={(e) => setReview(e.target.value)}
          placeholder="Entrez votre avis ici..."
          rows={4}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !review.trim()}>
          {loading ? 'Analyse en cours...' : 'Analyser'}
        </button>
      </form>

      {error && (
        <div className="error">
          {error}
        </div>
      )}

      {result && (
        <div className="result">
          <div className="rating">
            <span className="stars">{renderStars(result.rating)}</span>
            <span className="rating-number">{result.rating}/5</span>
          </div>
          <p className="explanation">{result.explanation}</p>
        </div>
      )}
    </div>
  )
}

export default App
