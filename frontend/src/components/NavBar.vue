<template>
  <nav class="navbar">
    <div class="navbar-inner">
      <span class="navbar-brand">Budget Tracker</span>
      <div class="navbar-links">
        <RouterLink to="/"         class="nav-link" active-class="nav-link--active" exact>Home</RouterLink>
        <RouterLink to="/category" class="nav-link" active-class="nav-link--active">Categories</RouterLink>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: #111827;
  border-bottom: 1px solid #2d3748;
  padding: 0 2rem;
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1400px;
  margin: 0 auto;
  height: 52px;
}

.navbar-brand {
  font-size: 1rem;
  font-weight: 600;
  color: #f9fafb;
  letter-spacing: 0.02em;
}

.navbar-links {
  display: flex;
  gap: 0.25rem;
}

.nav-link {
  color: #9ca3af;
  text-decoration: none;
  padding: 0.4rem 1rem;
  border-radius: 4px;
  font-size: 0.875rem;
  transition: color 0.15s;
}

.nav-link:hover {
  color: #f9fafb;
}

.nav-link--active {
  color: #fff;
  font-weight: 600;
  box-shadow: inset 0 -2px 0 #fff;
  font-weight: 600;
}
</style>
