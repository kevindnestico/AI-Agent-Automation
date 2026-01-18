Saucedemo Page Object Model - Python + Playwright
Este proyecto implementa un Page Object Model (POM) completo y robusto para automatizar pruebas en Saucedemo usando Python y Playwright Sync API.

📁 Estructura del Proyecto
project/
├── pages/
│   ├── __init__.py
│   ├── base_page.py
│   ├── login_page.py
│   ├── inventory_page.py
│   ├── cart_page.py
│   ├── checkout_info_page.py
│   ├── checkout_overview_page.py
│   └── checkout_complete_page.py
├── conftest.py
├── test_complete_purchase.py
└── README.md
🎯 Clases Implementadas
BasePage
Clase base con funcionalidad común para todos los Page Objects:

Navegación
Obtención de URL actual
Espera de URL
LoginPage
login(username, password) - Realizar login
get_error_message() - Obtener mensaje de error
verify_login_page_loaded() - Verificar carga de página
InventoryPage
add_to_cart_by_name(product_name) - Agregar producto al carrito
remove_from_cart_by_name(product_name) - Remover producto del carrito
go_to_cart() - Navegar al carrito
get_product_prices() - Obtener lista de precios
get_product_names() - Obtener nombres de productos
sort_products(sort_option) - Ordenar productos
get_cart_count() - Obtener cantidad de items en carrito
CartPage
remove_item(product_name) - Remover item del carrito
proceed_to_checkout() - Proceder al checkout
get_cart_item_count() - Obtener cantidad de items
get_cart_item_names() - Obtener nombres de items
is_cart_empty() - Verificar si el carrito está vacío
CheckoutInfoPage
fill_info(first_name, last_name, postal_code) - Llenar información
continue_to_overview() - Continuar a resumen
get_error_message() - Obtener mensaje de error
CheckoutOverviewPage
finish() - Finalizar compra
get_payment_summary() - Obtener resumen de pago
get_item_count() - Obtener cantidad de items
CheckoutCompletePage
get_thank_you_message() - Obtener mensaje de agradecimiento
verify_order_complete() - Verificar orden completada
go_back_home() - Volver al inicio
🔧 Características Técnicas
Locators Robustos
✅ get_by_role() - Acceso por rol semántico
✅ get_by_text() - Búsqueda por texto visible
✅ get_by_placeholder() - Búsqueda por placeholder
✅ get_by_test_id() - Acceso por test ID
Assertions con Playwright
✅ expect(locator).to_be_visible()
✅ expect(locator).to_have_text()
✅ expect(locator).to_be_enabled()
✅ expect(locator).not_to_be_visible()
Type Hints
Todas las clases y métodos incluyen type hints completos para mejor autocompletado y detección de errores.

Docstrings
Documentación completa en formato Google-style para todas las clases y métodos.

📦 Instalación
bash
# Instalar Playwright
pip install playwright pytest pytest-playwright

# Instalar navegadores
playwright install chromium
🚀 Ejecución
Ejecutar todos los tests
bash
pytest
Ejecutar suite específica
bash
pytest tests/test_login.py -v
pytest tests/test_inventory.py -v
pytest tests/test_cart.py -v
pytest tests/test_checkout_happy_path.py -v
pytest tests/test_checkout_negative.py -v
pytest tests/test_complete_purchase.py -v
Ejecutar un test específico
bash
pytest tests/test_checkout_happy_path.py::test_checkout_happy_path -v
Ejecutar con headed mode (ver navegador)
bash
pytest tests/test_login.py -v --headed
Ejecutar por markers
bash
# Solo tests smoke
pytest -m smoke -v

# Solo tests de regresión
pytest -m regression -v

# Excluir tests lentos
pytest -m "not slow" -v
Ejecutar en paralelo
bash
# Requiere: pip install pytest-xdist
pytest -n auto

# Especificar número de workers
pytest -n 4
Generar reporte HTML
bash
# Requiere: pip install pytest-html
pytest --html=reports/report.html --self-contained-html
Ver coverage
bash
# Requiere: pip install pytest-cov
pytest --cov=pages --cov-report=html
💡 Ejemplos de Uso
Ejemplo 1: Login y agregar productos
python
from pages.login_page import LoginPage
from pages.inventory_page import InventoryPage

def test_add_products(page):
    # Login
    login = LoginPage(page)
    login.navigate()
    login.login("standard_user", "secret_sauce")
    
    # Agregar productos
    inventory = InventoryPage(page)
    inventory.add_to_cart_by_name("Sauce Labs Backpack")
    
    assert inventory.get_cart_count() == 1
Ejemplo 2: Flujo completo de compra
Ver test_complete_purchase.py para un ejemplo completo del flujo end-to-end.

🎨 Fixtures Disponibles
browser
Browser de Chromium con configuración básica.

context
Contexto de navegador aislado con viewport personalizado.

page
Página individual para tests.

authenticated_page
Página ya autenticada (ahorra tiempo en tests que no prueban login).

📋 Suite de Tests Completa
tests/test_login.py (9 tests)
✅ Login exitoso con standard_user
✅ Credenciales inválidas (username, password)
✅ Campos vacíos (username, password, ambos)
✅ Usuario bloqueado (locked_out_user)
✅ Usuarios especiales (problem_user, performance_glitch_user)
tests/test_inventory.py (13 tests)
✅ Agregar items al carrito (single, múltiples, todos)
✅ Remover items del carrito
✅ Sorting (precio low-high, high-low, nombre A-Z, Z-A)
✅ Validación de productos y precios
✅ Navegación al carrito
tests/test_cart.py (10 tests)
✅ Visualización de items en carrito
✅ Remover items (individual, todos)
✅ Continuar comprando
✅ Proceder al checkout
✅ Persistencia de items después de navegación
✅ Carrito vacío
tests/test_checkout_happy_path.py (1 test)
✅ Flujo completo de checkout exitoso
tests/test_checkout_negative.py (12 tests)
✅ Campos vacíos en checkout (first name, last name, postal code)
✅ Cancelar checkout (info page, overview page)
✅ Caracteres especiales en nombres
✅ Nombres muy largos
✅ Valores numéricos en nombres
✅ Checkout desde carrito vacío
✅ Formato inválido de código postal
tests/test_complete_purchase.py (9 tests)
✅ Compra con 1 item
✅ Compra con múltiples items
✅ Compra con todos los items disponibles
✅ Compra con remoción de items
✅ Variaciones de información de cliente
✅ Verificación de cálculos de pago
✅ Retorno a inventario después de compra
✅ Compra con items ordenados
Total: 54 tests 🎯

🔍 Buenas Prácticas Implementadas
✅ Separación clara de responsabilidades
✅ Uso de locators robustos y mantenibles
✅ Validaciones explícitas con expect()
✅ Métodos reutilizables y autocontenidos
✅ Type hints completos
✅ Documentación exhaustiva
✅ Fixtures parametrizables
✅ Esperas implícitas y explícitas
🛠️ Personalización
Cambiar viewport
Edita conftest.py:

python
viewport={"width": 1920, "height": 1080}
Cambiar velocidad de ejecución
Edita el fixture browser:

python
browser = playwright.chromium.launch(
    headless=False,
    slow_mo=1000  # milisegundos
)
📚 Recursos
Playwright Python Docs
Saucedemo
Pytest Documentation
🤝 Contribuciones
Este POM es una base sólida y extensible. Puedes agregar:

Más Page Objects para otras páginas
Más métodos helper
Más validaciones
Integración con CI/CD
Reports con Allure
¡Happy Testing! 🧪