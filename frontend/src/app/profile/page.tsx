'use client'

import Link from 'next/link'
import { useState, useEffect } from 'react'
import Item from './item';


const apiUrl = process.env.apiUrl;
export default function Page() {
  const [data, setData] = useState(null)
  const [isLoading, setLoading] = useState(true)

  let profileUrl = '/api/profile';
  useEffect(() => {
    fetch(profileUrl)
      .then((res) => res.json())
      .then((data) => {
        console.log('DATA:', data)
        setData(data)
        setLoading(false)
      })
  }, [])

  if (isLoading) return <p>Loading...</p>
  if (!data) return <p>No profile data</p>

  return (
    <div>
      <h1>Profile</h1>
      {typeof data === 'object' && !Array.isArray(data) ? (
        Object.entries(data).map(([key, value]) => (
          <Item key={key} value={value} itemId={key} />
        ))
      ) : (
        <div>Data is not a dictionary</div>
      )}
    </div>
  )
}