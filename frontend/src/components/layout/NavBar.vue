<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <span class="navbar-brand">Budget Tracker</span>
      <div class="navbar-links">
        <RouterLink to="/"         class="nav-link" active-class="nav-link--active" exact>Home</RouterLink>
        <RouterLink to="/category" class="nav-link" active-class="nav-link--active">Categories</RouterLink>
        <RouterLink to="/subscriptions" class="nav-link" active-class="nav-link--active">Subscriptions</RouterLink>
        <RouterLink to="/settings" class="nav-link" active-class="nav-link--active">Settings</RouterLink>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(92deg, #0a1530 0%, #0d234f 58%, #0f3a84 100%);
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
  padding: 0 2rem;
  box-shadow: 0 12px 26px rgba(3, 9, 23, 0.26);
  backdrop-filter: blur(6px);
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1680px;
  margin: 0 auto;
  height: 60px;
}

.navbar-brand {
  font-size: 1.06rem;
  font-weight: 700;
  color: #f8fafc;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.navbar-links {
  display: flex;
  gap: 0.35rem;
  padding: 0.22rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.35);
  border: 1px solid rgba(148, 163, 184, 0.24);
}

.nav-link {
  color: #cbd5e1;
  text-decoration: none;
  padding: 0.42rem 0.94rem;
  border-radius: 999px;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background var(--transition), color var(--transition), box-shadow var(--transition);
}

.nav-link:hover {
  color: #f8fafc;
  background: rgba(148, 163, 184, 0.14);
}

.nav-link--active {
  color: #f8fafc;
  background: linear-gradient(135deg, #2958c8 0%, #1e4ebd 100%);
  border: 1px solid rgba(191, 219, 254, 0.4);
  box-shadow: 0 10px 18px rgba(15, 62, 168, 0.36);
  font-weight: 600;
}
</style>

