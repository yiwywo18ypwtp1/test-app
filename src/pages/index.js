import { useState, useEffect } from 'react';
import axios from 'axios';
import AddCatForm from '../components/AddCatForm';
import CatList from '../components/CatList';

export default function Home() {
  const [cats, setCats] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchCats = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/cats/`);
      setCats(res.data.cats || []);
    } catch (err) {
      console.error('Loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCats(); }, []);

  const handleAddCat = async (newCat) => {
    try {
      await axios.post(`http://localhost:8000/cat/`, newCat);
      fetchCats();
    } catch (err) {
      console.error('Adding error:', err);
    }
  };

  const handleDelete = async (catName) => {
    try {
      await axios.delete(`http://localhost:8000/cat/`, { params: { catname: catName } });
      fetchCats();
    } catch (err) {
      console.error('Deleting error:', err);
    }
  };

  const handleSalaryUpdate = async () => {
    await fetchCats();
  };

  return (
    <div className="container">
      <h1>Spy Cats Dashboard</h1>

      <div className="content">
        <AddCatForm onSubmit={handleAddCat} />
        {loading ? (
          <p>Loading...</p>
        ) : (
          <CatList
            cats={cats}
            onDelete={handleDelete}
            onSalaryUpdate={handleSalaryUpdate}
          />
        )}
      </div>

      <style jsx>{`
        html {
          background-color: white;
        }
        .container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
          font-family: Arial, sans-serif;
        }
        h1 {
          color: #333;
          text-align: center;
        }
        .content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-top: 20px;
        }
      `}</style>
    </div>
  );
}