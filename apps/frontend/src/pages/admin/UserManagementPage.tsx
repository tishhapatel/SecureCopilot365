import React, { useState, useEffect } from 'react';
import { api } from '../../lib/api';
import { UserResponse } from '../../lib/types';
import { UserPlus, UserCheck, UserX, Trash2, Shield, Mail, RefreshCw, Layers } from 'lucide-react';

export default function UserManagementPage() {
  const [users, setUsers] = useState<UserResponse[]>([]);
  const [roles, setRoles] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // New User Form State
  const [showForm, setShowForm] = useState(false);
  const [email, setEmail] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState('General Employee');
  const [department, setDepartment] = useState('Security');

  const fetchUsersAndRoles = async () => {
    setLoading(true);
    setError(null);
    try {
      const [usersData, rolesData] = await Promise.all([
        api.getUsers(),
        api.getRoles()
      ]);
      setUsers(usersData);
      setRoles(rolesData);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch user directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsersAndRoles();
  }, []);

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await api.createUser({
        email,
        display_name: displayName,
        password,
        role_name: selectedRole,
        department
      });
      // Reset Form
      setEmail('');
      setDisplayName('');
      setPassword('');
      setSelectedRole('General Employee');
      setDepartment('Security');
      setShowForm(false);
      // Refresh directory
      await fetchUsersAndRoles();
    } catch (err: any) {
      setError(err.message || 'Failed to register new tenant account.');
    }
  };

  const handleRoleChange = async (userId: string, roleName: string) => {
    setError(null);
    try {
      await api.updateUserRole(userId, roleName);
      await fetchUsersAndRoles();
    } catch (err: any) {
      setError(err.message || 'Failed to modify role allocation.');
    }
  };

  const handleToggleActivation = async (userId: string, currentStatus: boolean) => {
    setError(null);
    try {
      await api.updateUserActivation(userId, !currentStatus);
      await fetchUsersAndRoles();
    } catch (err: any) {
      setError(err.message || 'Failed to toggle activation state.');
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!window.confirm('Are you sure you want to terminate this user profile? This action is irreversible.')) {
      return;
    }
    setError(null);
    try {
      await api.deleteUser(userId);
      await fetchUsersAndRoles();
    } catch (err: any) {
      setError(err.message || 'Failed to remove user account.');
    }
  };

  return (
    <div className="flex-1 p-6 md:p-8 bg-[#0a0d16] overflow-y-auto space-y-6">
      
      {/* Header section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white tracking-wide font-outfit uppercase">
            User Directory Management
          </h1>
          <p className="text-xs text-gray-400">
            Provision roles, manage active states, and monitor departments in the active tenant.
          </p>
        </div>
        
        <div className="flex items-center gap-2">
          <button
            onClick={fetchUsersAndRoles}
            className="p-2.5 bg-darkCard hover:bg-[#1a2336] border border-darkBorder rounded-xl text-gray-400 hover:text-white transition"
          >
            <RefreshCw size={16} />
          </button>
          <button
            onClick={() => setShowForm(!showForm)}
            className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-cyberBlue to-cyberPurple text-white rounded-xl text-xs font-bold transition duration-300 shadow-glow"
          >
            <UserPlus size={16} />
            {showForm ? 'Cancel Creation' : 'Register User'}
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 rounded-xl text-xs font-semibold">
          {error}
        </div>
      )}

      {/* Register User Form */}
      {showForm && (
        <form onSubmit={handleCreateUser} className="p-6 rounded-3xl bg-darkCard border border-darkBorder space-y-4 max-w-2xl animate-fadeIn">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Register New Profile
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-[10px] text-gray-400 uppercase tracking-widest mb-1.5 font-mono">Email Address</label>
              <div className="relative">
                <Mail size={14} className="absolute left-3.5 top-3.5 text-gray-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@securecop.com"
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-[#0a0d16] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] text-gray-400 uppercase tracking-widest mb-1.5 font-mono">Display Name</label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Sarah Connor"
                required
                className="w-full px-4 py-2.5 bg-[#0a0d16] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
              />
            </div>

            <div>
              <label className="block text-[10px] text-gray-400 uppercase tracking-widest mb-1.5 font-mono">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="password123"
                required
                className="w-full px-4 py-2.5 bg-[#0a0d16] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
              />
            </div>

            <div>
              <label className="block text-[10px] text-gray-400 uppercase tracking-widest mb-1.5 font-mono">Department</label>
              <input
                type="text"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="Security Operations"
                className="w-full px-4 py-2.5 bg-[#0a0d16] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
              />
            </div>

            <div>
              <label className="block text-[10px] text-gray-400 uppercase tracking-widest mb-1.5 font-mono">Security Role</label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                className="w-full px-4 py-2.5 bg-[#0a0d16] border border-darkBorder rounded-xl text-xs text-white focus:outline-none focus:border-cyberBlue transition"
              >
                {roles.map((r) => (
                  <option key={r.id} value={r.role_name}>{r.role_name}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="px-5 py-2.5 bg-gradient-to-r from-cyberBlue to-cyberPurple text-white rounded-xl text-xs font-bold transition duration-300 shadow-glow"
          >
            Provision Active Credentials
          </button>
        </form>
      )}

      {/* Users directory table */}
      <div className="bg-darkCard border border-darkBorder rounded-3xl overflow-hidden shadow-lg">
        {loading ? (
          <div className="p-12 text-center text-gray-400 text-xs font-mono uppercase tracking-widest animate-pulse">
            Querying User Directory database...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-left">
              <thead>
                <tr className="border-b border-darkBorder bg-[#0c101d] text-gray-400 text-[10px] uppercase font-mono tracking-wider">
                  <th className="p-4 pl-6">Display Name</th>
                  <th className="p-4">Email</th>
                  <th className="p-4">Department</th>
                  <th className="p-4">Tenant Domain</th>
                  <th className="p-4">Security Role</th>
                  <th className="p-4 text-center">Status</th>
                  <th className="p-4 pr-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-darkBorder/40">
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-8 text-center text-xs text-gray-500 font-mono">
                      No active users registered in this tenant environment.
                    </td>
                  </tr>
                ) : (
                  users.map((u) => (
                    <tr key={u.id} className="hover:bg-darkCard/50 text-xs transition duration-150">
                      <td className="p-4 pl-6 font-semibold text-white">{u.display_name}</td>
                      <td className="p-4 text-gray-400 font-mono">{u.email}</td>
                      <td className="p-4 text-gray-300">{u.department || 'General'}</td>
                      <td className="p-4 font-mono text-[10px] text-cyberBlue">{u.tenant_id}</td>
                      <td className="p-4">
                        <div className="relative">
                          <select
                            value={u.role.role_name}
                            onChange={(e) => handleRoleChange(u.id, e.target.value)}
                            className="bg-[#0a0d16] border border-darkBorder hover:border-cyberPurple/50 px-2 py-1.5 rounded-lg text-xs text-white focus:outline-none transition cursor-pointer"
                          >
                            {roles.map((r) => (
                              <option key={r.id} value={r.role_name}>{r.role_name}</option>
                            ))}
                          </select>
                        </div>
                      </td>
                      <td className="p-4 text-center">
                        <button
                          onClick={() => handleToggleActivation(u.id, u.is_active)}
                          className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold border transition ${
                            u.is_active
                              ? 'bg-cyberGreen/10 border-cyberGreen/20 text-cyberGreen shadow-glowGreen'
                              : 'bg-red-500/10 border-red-500/20 text-red-400'
                          }`}
                        >
                          {u.is_active ? (
                            <>
                              <UserCheck size={10} /> Active
                            </>
                          ) : (
                            <>
                              <UserX size={10} /> Suspended
                            </>
                          )}
                        </button>
                      </td>
                      <td className="p-4 pr-6 text-right">
                        <button
                          onClick={() => handleDeleteUser(u.id)}
                          className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-500/10 rounded-xl transition duration-200"
                          title="Terminate Account"
                        >
                          <Trash2 size={14} />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
