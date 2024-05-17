from hybridagi import CodeInterpreterUtility

def test_code_interpreter():
    interpreter = CodeInterpreterUtility()

    code = \
"""
# Générer des données aléatoires
x = np.arange(10)  # Générer une séquence de 10 nombres (0 à 9)
y = np.random.rand(10)  # Générer 10 nombres aléatoires

# Créer un graphique
plt.plot(x, y, marker='o')  # Tracer les données avec des points marqués par des cercles

# Ajouter des titres et des étiquettes
plt.title('Graphique Simple avec Matplotlib')
plt.xlabel('Index')
plt.ylabel('Valeur aléatoire')

# Afficher le graphique
plt.show()
"""
    result, plots, err = interpreter.add_and_run(code)
    assert len(plots) == 1
    assert result == ""
    assert err == False