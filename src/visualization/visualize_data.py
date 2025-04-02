import oracledb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import json
import time
import shutil

def datetime_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def debug_print(message, data=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if data is not None:
        print(f"Data: {data}")

def get_table_stats(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count

def execute_query_to_df(cursor, query):
    cursor.execute(query)
    columns = [desc[0].lower() for desc in cursor.description]
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)

def plot_students_by_house(cursor):
    query = """
    SELECT h.name as house_name, COUNT(s.id) as student_count
    FROM houses h
    LEFT JOIN students s ON h.id = s.house_id
    GROUP BY h.name
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(8, 4))
    sns.barplot(data=df, x='house_name', y='student_count')
    plt.title('Number of Students per House')
    plt.xlabel('House')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('docs/visualizations/students_by_house.png')
    plt.close()

def plot_grades_distribution(cursor):
    query = """
    SELECT g.value as grade_value, COUNT(*) as count
    FROM grades g
    GROUP BY g.value
    ORDER BY 
        CASE g.value
            WHEN 'O' THEN 1
            WHEN 'E' THEN 2
            WHEN 'A' THEN 3
            WHEN 'P' THEN 4
            WHEN 'D' THEN 5
            WHEN 'T' THEN 6
        END
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(8, 4))
    sns.barplot(data=df, x='grade_value', y='count')
    plt.title('Grade Distribution')
    plt.xlabel('Grade')
    plt.ylabel('Number of Grades')
    plt.tight_layout()
    plt.savefig('docs/visualizations/grades_distribution.png')
    plt.close()

def plot_points_by_house(cursor):
    query = """
    SELECT h.name as house_name, SUM(p.value) as total_points
    FROM houses h
    JOIN students s ON h.id = s.house_id
    JOIN points p ON s.id = p.student_id
    GROUP BY h.name
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(8, 4))
    sns.barplot(data=df, x='house_name', y='total_points')
    plt.title('Total Points per House')
    plt.xlabel('House')
    plt.ylabel('Total Points')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('docs/visualizations/points_by_house.png')
    plt.close()

def plot_subjects_popularity(cursor):
    query = """
    SELECT s.name as subject_name, COUNT(ss.student_id) as student_count
    FROM subjects s
    JOIN students_subjects ss ON s.id = ss.subject_id
    GROUP BY s.name
    ORDER BY COUNT(ss.student_id) DESC
    FETCH FIRST 10 ROWS ONLY
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(8, 4))
    sns.barplot(data=df, x='student_count', y='subject_name')
    plt.title('Top 10 Most Popular Subjects')
    plt.xlabel('Number of Students')
    plt.ylabel('Subject')
    plt.tight_layout()
    plt.savefig('docs/visualizations/subjects_popularity.png')
    plt.close()

def plot_gender_distribution(cursor):
    query = """
    SELECT gender, COUNT(*) as count
    FROM students
    GROUP BY gender
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(6, 6))
    plt.pie(df['count'], labels=df['gender'], autopct='%1.1f%%')
    plt.title('Gender Distribution Among Students')
    plt.tight_layout()
    plt.savefig('docs/visualizations/gender_distribution.png')
    plt.close()

def plot_quidditch_teams(cursor):
    query = """
    SELECT h.name as house_name, COUNT(qtm.id) as team_size
    FROM houses h
    LEFT JOIN students s ON h.id = s.house_id
    LEFT JOIN quidditch_team_members qtm ON s.id = qtm.student_id
    GROUP BY h.name
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(8, 4))
    sns.barplot(data=df, x='house_name', y='team_size')
    plt.title('Quidditch Team Size by House')
    plt.xlabel('House')
    plt.ylabel('Team Size')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('docs/visualizations/quidditch_teams.png')
    plt.close()

def run_performance_analysis(cursor, config=None):
    print("Running performance analysis...")
    results = []
    
    try:
        # Simple SELECT
        start_time = time.time()
        cursor.execute("SELECT * FROM students WHERE ROWNUM <= 2137")
        rows = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Completed Simple SELECT in {execution_time:.4f} seconds")
        results.append({
            'name': 'Simple SELECT',
            'execution_time': execution_time,
            'description': 'Basic select query on students table',
            'rows': len(rows)
        })

        # Complex JOIN
        start_time = time.time()
        cursor.execute("""
            SELECT s.name, s.surname, g.value, sub.name as subject
            FROM students s
            JOIN grades g ON s.id = g.student_id
            JOIN subjects sub ON g.subject_id = sub.id
            WHERE ROWNUM <= 1000
        """)
        rows = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Completed Complex JOIN in {execution_time:.4f} seconds")
        results.append({
            'name': 'Complex JOIN',
            'execution_time': execution_time,
            'description': 'Complex join between students, grades, and subjects',
            'rows': len(rows)
        })

        # Aggregation
        start_time = time.time()
        cursor.execute("""
            SELECT h.name, COUNT(s.id) as student_count, AVG(LENGTH(s.surname)) as avg_surname_length
            FROM houses h
            LEFT JOIN students s ON h.id = s.house_id
            GROUP BY h.name
            HAVING COUNT(s.id) > 0
        """)
        rows = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Completed Aggregation in {execution_time:.4f} seconds")
        results.append({
            'name': 'Aggregation',
            'execution_time': execution_time,
            'description': 'Complex aggregation with grouping and having',
            'rows': len(rows)
        })

        # Nested Subquery
        start_time = time.time()
        cursor.execute("""
            SELECT s.name, s.surname
            FROM students s
            WHERE s.id IN (
                SELECT student_id
                FROM grades g
                WHERE g.value = 'O'
                AND ROWNUM <= 40
            )
        """)
        rows = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Completed Nested Subquery in {execution_time:.4f} seconds")
        results.append({
            'name': 'Nested Subquery',
            'execution_time': execution_time,
            'description': 'Complex nested subquery with multiple conditions',
            'rows': len(rows)
        })

        # Transaction - Batch Insert
        try:
            start_time = time.time()
            cursor.execute("SAVEPOINT before_test")
            
            for i in range(100):
                cursor.execute("""
                    INSERT INTO grades (id, value, award_date, student_id, subject_id, teacher_id)
                    SELECT 
                        grades_seq.NEXTVAL,
                        'A',
                        SYSDATE,
                        (SELECT id FROM students WHERE ROWNUM = 1),
                        (SELECT id FROM subjects WHERE ROWNUM = 1),
                        (SELECT id FROM teachers WHERE ROWNUM = 1)
                    FROM dual
                """)
            
            cursor.execute("ROLLBACK TO SAVEPOINT before_test")
            execution_time = time.time() - start_time
            print(f"Completed Transaction - Batch Insert in {execution_time:.4f} seconds")
            results.append({
                'name': 'Transaction - Batch Insert',
                'execution_time': execution_time,
                'description': 'Insert multiple grades with transaction control',
                'rows': 100
            })
        except Exception as e:
            print(f"Error in Transaction - Batch Insert: {str(e)}")
            results.append({
                'name': 'Transaction - Batch Insert',
                'execution_time': None,
                'description': 'Insert multiple grades with transaction control',
                'rows': 0,
                'error': str(e)
            })

        # Transaction - Batch Update
        try:
            start_time = time.time()
            cursor.execute("SAVEPOINT before_test")
            
            cursor.execute("""
                UPDATE grades
                SET value = 'O'
                WHERE id IN (
                    SELECT id FROM grades
                    WHERE ROWNUM <= 1000
                )
            """)
            
            cursor.execute("ROLLBACK TO SAVEPOINT before_test")
            execution_time = time.time() - start_time
            print(f"Completed Transaction - Batch Update in {execution_time:.4f} seconds")
            results.append({
                'name': 'Transaction - Batch Update',
                'execution_time': execution_time,
                'description': 'Update multiple grades with transaction control',
                'rows': 1000
            })
        except Exception as e:
            print(f"Error in Transaction - Batch Update: {str(e)}")
            results.append({
                'name': 'Transaction - Batch Update',
                'execution_time': None,
                'description': 'Update multiple grades with transaction control',
                'rows': 0,
                'error': str(e)
            })

        # Transaction - Complex Delete
        try:
            start_time = time.time()
            cursor.execute("SAVEPOINT before_test")
            
            cursor.execute("""
                DELETE FROM grades
                WHERE student_id IN (
                    SELECT id FROM students
                    WHERE house_id = (
                        SELECT id FROM houses
                        WHERE name = 'Slytherin'
                    )
                )
                AND ROWNUM <= 1000
            """)
            
            cursor.execute("ROLLBACK TO SAVEPOINT before_test")
            execution_time = time.time() - start_time
            print(f"Completed Transaction - Complex Delete in {execution_time:.4f} seconds")
            results.append({
                'name': 'Transaction - Complex Delete',
                'execution_time': execution_time,
                'description': 'Delete with complex conditions and restore data',
                'rows': 1000
            })
        except Exception as e:
            print(f"Error in Transaction - Complex Delete: {str(e)}")
            results.append({
                'name': 'Transaction - Complex Delete',
                'execution_time': None,
                'description': 'Delete with complex conditions and restore data',
                'rows': 0,
                'error': str(e)
            })

        # Full Table Scan Analysis
        start_time = time.time()
        cursor.execute("""
            SELECT value, COUNT(*) as count
            FROM grades
            GROUP BY value
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Completed Full Table Scan Analysis in {execution_time:.4f} seconds")
        results.append({
            'name': 'Full Table Scan Analysis',
            'execution_time': execution_time,
            'description': 'Analyze grade distribution with full table scan',
            'rows': len(rows)
        })

        # Index Scan Analysis
        start_time = time.time()
        cursor.execute("""
            SELECT s.name, s.surname, h.name as house, COUNT(g.id) as grades_count
            FROM students s
            JOIN houses h ON s.house_id = h.id
            LEFT JOIN grades g ON s.id = g.student_id
            GROUP BY s.name, s.surname, h.name
            HAVING COUNT(g.id) > 0
            AND ROWNUM <= 50
        """)
        rows = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Completed Index Scan Analysis in {execution_time:.4f} seconds")
        results.append({
            'name': 'Index Scan Analysis',
            'execution_time': execution_time,
            'description': 'Analyze student performance using indexes',
            'rows': len(rows)
        })

        # Complex Analytics
        start_time = time.time()
        cursor.execute("""
            WITH student_grades AS (
                SELECT 
                    s.id,
                    s.name,
                    s.surname,
                    h.name as house,
                    COUNT(g.id) as grades_count,
                    COUNT(CASE WHEN g.value = 'O' THEN 1 END) as outstanding_grades,
                    ROW_NUMBER() OVER (PARTITION BY h.id ORDER BY COUNT(CASE WHEN g.value = 'O' THEN 1 END) DESC) as house_rank
                FROM students s
                JOIN houses h ON s.house_id = h.id
                LEFT JOIN grades g ON s.id = g.student_id
                GROUP BY s.id, s.name, s.surname, h.name, h.id
            )
            SELECT *
            FROM student_grades
            WHERE house_rank <= 50
            ORDER BY house, house_rank
        """)
        rows = cursor.fetchall()
        execution_time = time.time() - start_time
        print(f"Completed Complex Analytics in {execution_time:.4f} seconds")
        results.append({
            'name': 'Complex Analytics',
            'execution_time': execution_time,
            'description': 'Complex analytical query with window functions',
            'rows': len(rows)
        })

    except Exception as e:
        print(f"Error in performance analysis: {str(e)}")
        
    return results

def generate_performance_summary(performance_results):
    return '\n'.join(f"""
        <tr>
            <td>{result['name']}</td>
            <td>{result['description']}</td>
            <td>{result['execution_time'] if result['execution_time'] is not None else 'Error'} seconds</td>
            <td>{result['rows']}</td>
            <td>
                <button class="detail-button" onclick="toggleSection('details-{result['name'].lower().replace(" ", "-")}')">
                    Show Details
                </button>
            </td>
        </tr>
        <tr id="details-{result['name'].lower().replace(" ", "-")}" class="details-row" style="display: none;">
            <td colspan="5">
                <div class="details-content">
                    <pre>{json.dumps(result['data'], indent=2, default=datetime_handler) if 'data' in result else result.get('error', 'No data available')}</pre>
                </div>
            </td>
        </tr>
    """ for result in performance_results)

def generate_html_report(stats, performance_results):
    # Create HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
        <title>Hogwarts Database Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            h1, h2 {
                color: #1a237e;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #1a237e;
                color: white;
            }
            tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            .section {
                margin: 30px 0;
                padding: 20px;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .collapsible {
                background-color: #1a237e;
                color: white;
                cursor: pointer;
                padding: 18px;
                width: 100%;
                border: none;
                text-align: left;
                outline: none;
                font-size: 15px;
                border-radius: 5px;
                margin: 10px 0;
            }
            .active, .collapsible:hover {
                background-color: #0d47a1;
            }
            .content {
                padding: 0 18px;
                display: none;
                overflow: hidden;
                background-color: #f1f1f1;
                border-radius: 0 0 5px 5px;
            }
            .schema-img {
                max-width: 100%;
                height: auto;
                cursor: pointer;
                transition: transform 0.3s ease;
            }
            .schema-img:hover {
                transform: scale(1.05);
            }
            .visualization-img {
                max-width: 100%;
                height: auto;
                margin: 10px 0;
            }
            .wizard-section {
                background-color: #e3f2fd;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .wizard-button {
                background-color: #1a237e;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                margin: 5px;
                font-size: 14px;
            }
            .wizard-button:hover {
                background-color: #0d47a1;
            }
            .error {
                color: #d32f2f;
                background-color: #ffebee;
                padding: 10px;
                border-radius: 5px;
                margin: 5px 0;
            }
            .success {
                color: #1b5e20;
                background-color: #e8f5e9;
                padding: 10px;
                border-radius: 5px;
                margin: 5px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hogwarts Database Report</h1>
            
            <!-- Database Statistics -->
            <button type="button" class="collapsible">Database Statistics</button>
            <div class="content">
                <table>
                    <tr>
                        <th>Table</th>
                        <th>Row Count</th>
                    </tr>
    """

    # Add statistics rows
    for table, count in stats.items():
        html_content += f"""
                    <tr>
                        <td>{table}</td>
                        <td>{count}</td>
                    </tr>
        """

    html_content += """
                </table>
            </div>

            <!-- Database Schema -->
            <button type="button" class="collapsible">Database Schema</button>
            <div class="content">
                <h3>Entity Relationship Diagram</h3>
                <img src="HogwartRelations.png" alt="Database Relations" class="schema-img" onclick="window.open(this.src)">
                <h3>Database Schema</h3>
                <img src="schema.png" alt="Database Schema" class="schema-img" onclick="window.open(this.src)">
            </div>

            <!-- Visualizations -->
            <button type="button" class="collapsible">Visualizations</button>
            <div class="content">
                <h3>Students by House</h3>
                <img src="visualizations/students_by_house.png" alt="Students by House" class="visualization-img">
                <h3>Grades Distribution</h3>
                <img src="visualizations/grades_distribution.png" alt="Grades Distribution" class="visualization-img">
                <h3>Subjects Popularity</h3>
                <img src="visualizations/subjects_popularity.png" alt="Subjects Popularity" class="visualization-img">
                <h3>Points by House</h3>
                <img src="visualizations/points_by_house.png" alt="Points by House" class="visualization-img">
                <h3>Gender Distribution</h3>
                <img src="visualizations/gender_distribution.png" alt="Gender Distribution" class="visualization-img">
                <h3>Quidditch Teams</h3>
                <img src="visualizations/quidditch_teams.png" alt="Quidditch Teams" class="visualization-img">
            </div>

            <!-- Performance Analysis -->
            <button type="button" class="collapsible">Performance Analysis</button>
            <div class="content">
                <table>
                    <tr>
                        <th>Query Type</th>
                        <th>Description</th>
                        <th>Execution Time</th>
                        <th>Rows Processed</th>
                    </tr>
    """

    # Add performance results
    for result in performance_results:
        execution_time = f"{result['execution_time']:.4f} seconds" if result['execution_time'] is not None else "Error"
        status_class = "error" if result.get('error') else "success"
        html_content += f"""
                    <tr class="{status_class}">
                        <td>{result['name']}</td>
                        <td>{result['description']}</td>
                        <td>{execution_time}</td>
                        <td>{result['rows']}</td>
                    </tr>
        """

    html_content += """
                </table>
            </div>

            <!-- Data Wizard -->
            <button type="button" class="collapsible">Data Wizard 🧙‍♂️</button>
            <div class="content wizard-section">
                <h3>Generate and Manage Data</h3>
                <p>Use these magical buttons to manage your Hogwarts database:</p>
                <button onclick="generateConfig()" class="wizard-button">Generate Configuration 📝</button>
                <button onclick="generateData()" class="wizard-button">Generate Test Data 🎲</button>
                <button onclick="importData()" class="wizard-button">Import Data to Database 📥</button>
                <button onclick="clearDatabase()" class="wizard-button">Clear Database 🧹</button>
                <button onclick="runTests()" class="wizard-button">Run Performance Tests ⚡</button>
                <div id="wizardStatus"></div>
            </div>

            <script>
                // Collapsible sections
                var coll = document.getElementsByClassName("collapsible");
                for (var i = 0; i < coll.length; i++) {
                    coll[i].addEventListener("click", function() {
                        this.classList.toggle("active");
                        var content = this.nextElementSibling;
                        if (content.style.display === "block") {
                            content.style.display = "none";
                        } else {
                            content.style.display = "block";
                        }
                    });
                }

                // Wizard functions
                async function showStatus(message, isError = false) {
                    const statusDiv = document.getElementById('wizardStatus');
                    statusDiv.innerHTML = `<div class="${isError ? 'error' : 'success'}">${message}</div>`;
                }

                async function makeRequest(endpoint, message) {
                    try {
                        const response = await fetch(endpoint, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                        });
                        const data = await response.json();
                        
                        if (data.status === 'success') {
                            showStatus(data.loading_message || message);
                            if (endpoint === '/run_tests') {
                                setTimeout(() => window.location.reload(), 2000);
                            }
                        } else {
                            showStatus(data.message || 'An error occurred', true);
                        }
                    } catch (error) {
                        showStatus(`Error: ${error.message}`, true);
                    }
                }

                async function generateConfig() {
                    await makeRequest('/generate_config', '🧙‍♂️ Configuration generated successfully!');
                }

                async function generateData() {
                    await makeRequest('/generate_data', '🎲 Test data generated successfully!');
                }

                async function importData() {
                    await makeRequest('/import_data', '📥 Data imported successfully!');
                }

                async function clearDatabase() {
                    if (confirm('Are you sure you want to clear the database? This action cannot be undone!')) {
                        await makeRequest('/clear_database', '🧹 Database cleared successfully!');
                    }
                }

                async function runTests() {
                    await makeRequest('/run_tests', '⚡ Running performance tests...');
                }

                // Open first section by default
                document.getElementsByClassName("collapsible")[0].click();
            </script>
        </div>
    </body>
    </html>
    """

    # Save the report
    with open("docs/hogwarts_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def generate_placeholder_images():
    """Generate placeholder schema images if they don't exist"""
    import matplotlib.pyplot as plt
    
    # Create schema.png
    plt.figure(figsize=(10, 6))
    plt.text(0.5, 0.5, 'Database Schema', ha='center', va='center', fontsize=20)
    plt.axis('off')
    plt.savefig('schema.png')
    plt.close()
    
    # Create HogwartRelations.png
    plt.figure(figsize=(10, 6))
    plt.text(0.5, 0.5, 'Hogwarts Relations', ha='center', va='center', fontsize=20)
    plt.axis('off')
    plt.savefig('HogwartRelations.png')
    plt.close()

def copy_schema_images():
    """Copy schema images to docs directory"""
    # Generate placeholder images if they don't exist
    if not os.path.exists('schema.png') or not os.path.exists('HogwartRelations.png'):
        generate_placeholder_images()
    
    # Copy images to docs directory
    shutil.copy2('schema.png', 'docs/schema.png')
    shutil.copy2('HogwartRelations.png', 'docs/HogwartRelations.png')

def main():
    # Database connection configuration
    connection_string = "SYSTEM/admin@localhost:1521/XE"
    
    try:
        # Connect to database
        connection = oracledb.connect(connection_string)
        cursor = connection.cursor()
        debug_print("Connected to database")
        
        # Create visualizations directory
        os.makedirs('docs/visualizations', exist_ok=True)
        
        # Copy schema images
        copy_schema_images()
        
        # Get statistics
        debug_print("Getting statistics...")
        stats = {
            'teachers': get_table_stats(cursor, 'teachers'),
            'houses': get_table_stats(cursor, 'houses'),
            'dormitories': get_table_stats(cursor, 'dormitories'),
            'students': get_table_stats(cursor, 'students'),
            'subjects': get_table_stats(cursor, 'subjects'),
            'grades': get_table_stats(cursor, 'grades'),
            'points': get_table_stats(cursor, 'points'),
            'quidditch': get_table_stats(cursor, 'quidditch_team_members')
        }
        
        # Generate visualizations
        debug_print("Generating visualizations...")
        plot_students_by_house(cursor)
        plot_grades_distribution(cursor)
        plot_points_by_house(cursor)
        plot_subjects_popularity(cursor)
        plot_gender_distribution(cursor)
        plot_quidditch_teams(cursor)
        
        # Run performance analysis
        performance_results = run_performance_analysis(cursor)
        
        # Generate HTML report
        debug_print("Generating HTML report...")
        generate_html_report(stats, performance_results)
        
        debug_print("\nSUMMARY:")
        for table, count in stats.items():
            debug_print(f"{table}: {count} records")
        
        debug_print("\nReport has been generated in docs/hogwarts_report.html")
        
    except Exception as e:
        debug_print(f"ERROR: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            debug_print("Database connection closed")

if __name__ == "__main__":
    main() 