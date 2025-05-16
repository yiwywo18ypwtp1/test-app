import { useState } from 'react';
import axios from 'axios';

export default function CatList({ cats, onDelete, onSalaryUpdate }) {
  const [editingCat, setEditingCat] = useState(null);
  const [newSalary, setNewSalary] = useState('');

  const handleSalaryUpdate = (cat) => {
    setEditingCat(cat);
    setNewSalary(cat.salary);
  };

  const handleSave = async () => {
    try {
      await axios.patch('http://localhost:8000/cat/', null, {
        params: {
          catname: editingCat.catname,
          salary: Number(newSalary)
        },
      });
      setEditingCat(null);
      onSalaryUpdate();
    } catch (err) {
      console.error('Error:', err.response?.data);
    }
  };

  return (
    <div className="cat-list">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Experience</th>
            <th>Breed</th>
            <th>Salary</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {cats.map(cat => (
            <tr key={cat.catname}>
              <td>{cat.catname}</td>
              <td>{cat.experience} лет</td>
              <td>{cat.breed}</td>
              <td>${cat.salary}</td>
              <td className="actions">
                <button
                  onClick={() => handleSalaryUpdate(cat)}
                  className="edit-btn"
                >
                  Edit salary
                </button>
                <button
                  onClick={() => onDelete(cat.catname)}
                  className="delete-btn"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {editingCat && (
        <div className="modal">
          <div className="modal-content">
            <h3>Change salary for: {editingCat.name}</h3>
            <input
              type="number"
              value={newSalary}
              onChange={(e) => setNewSalary(e.target.value)}
            />
            <div className="modal-buttons">
              <button onClick={handleSave}>Save</button>
              <button onClick={() => setEditingCat(null)}>Cancel</button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .cat-list {
          background: white;
          border-radius: 8px;
          overflow: hidden;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        table {
          width: 100%;
          border-collapse: collapse;
        }
        th, td {
          padding: 12px 15px;
          text-align: left;
          border-bottom: 1px solid #ddd;
          color: #000;
        }
        th {
          background-color: #f2f2f2;
        }
        .actions {
          display: flex;
          gap: 5px;
        }
        button {
          padding: 5px 10px;
          border: none;
          border-radius: 3px;
          cursor: pointer;
        }
        .edit-btn {
          background: #2196F3;
          color: white;
        }
        .delete-btn {
          background: #f44336;
          color: white;
        }
        .modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .modal-content {
          background: white;
          padding: 20px;
          border-radius: 5px;
          width: 300px;
        }
        .modal-buttons {
          display: flex;
          justify-content: flex-end;
          gap: 10px;
          margin-top: 15px;
        }
      `}</style>
    </div>
  );
}