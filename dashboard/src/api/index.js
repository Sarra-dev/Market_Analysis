import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:8000',
});

export const getOverview    = () => API.get('/stats/overview');
export const getByCountry   = () => API.get('/stats/by-country');
export const getByContract  = () => API.get('/stats/by-contract');
export const getTopSkills   = () => API.get('/stats/top-skills');
export const getTopCompanies= () => API.get('/stats/top-companies');
export const getByDate      = () => API.get('/stats/by-date');
export const getJobs        = (params) => API.get('/jobs/', { params });
export const getJob         = (id) => API.get(`/jobs/${id}`);