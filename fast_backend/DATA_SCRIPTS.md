# Database Population Scripts

This directory contains several scripts for populating and managing the database with dummy data for development and testing.

## Scripts Overview

### 1. `generate_data.py` - Comprehensive Data Generation
The main script for creating realistic sample data.

```bash
# Generate default data (15 users, all sample cards, 20 decks)
python -m app.generate_data

# Generate custom amounts
python -m app.generate_data --users 50 --cards 200 --decks 30

# Clear existing data and generate new
python -m app.generate_data --clear --users 25

# Generate only cards (uses all sample card data)
python -m app.generate_data --users 0 --decks 0
```

**Features:**
- Creates realistic user accounts with proper password hashing
- Generates diverse cards inspired by trading card games
- Creates themed decks with meaningful descriptions
- Establishes deck-card relationships with realistic quantities
- First user is always an admin with login credentials shown

### 2. `quick_populate.py` - Fast Test Data
Quick script for minimal but sufficient test data.

```bash
# Creates 5 users, 20 cards, 5 decks with relationships
python -m app.quick_populate
```

**What it creates:**
- 1 admin user: `admin@test.com` / `admin123`
- 4 regular test users with `test123` password
- 20 basic cards covering different types
- 5 themed decks with 10-15 cards each

### 3. `generate_mtg_cards.py` - MTG-Style Cards
Specialized script for creating Magic: The Gathering inspired cards.

```bash
# Generate 200 MTG-style cards (default)
python -m app.generate_mtg_cards

# Generate specific number of cards
python -m app.generate_mtg_cards --count 500

# Clear existing cards and generate new ones
python -m app.generate_mtg_cards --count 300 --clear
```

**Card Distribution:**
- 40% Creatures (with abilities like Flying, Trample, etc.)
- 30% Spells (Instants and Sorceries)
- 15% Artifacts (Equipment and utility artifacts)
- 10% Enchantments (Ongoing effects)
- 5% Lands (Mana sources)

### 4. `db_utils.py` - Database Management
Utility script for database maintenance and inspection.

```bash
# Show detailed database statistics
python -m app.db_utils --stats

# Show sample data from database
python -m app.db_utils --sample

# Clear all data
python -m app.db_utils --clear

# Export data to JSON file
python -m app.db_utils --export
python -m app.db_utils --export my_export.json

# Reset database (clear + quick populate)
python -m app.db_utils --reset
```

## Usage Examples

### Development Setup
```bash
# Quick setup for development
python -m app.quick_populate

# Login with: admin@test.com / admin123
```

### Testing Setup
```bash
# Comprehensive test data
python -m app.generate_data --clear --users 20 --decks 15

# Add lots of MTG-style cards
python -m app.generate_mtg_cards --count 400
```

### Production-Like Data
```bash
# Large dataset for performance testing
python -m app.generate_data --clear --users 100 --cards 1000 --decks 200
```

### Database Maintenance
```bash
# Check what's in the database
python -m app.db_utils --stats --sample

# Export backup before changes
python -m app.db_utils --export backup_$(date +%Y%m%d).json

# Clean slate
python -m app.db_utils --reset
```

## Data Structure

### Users
- **Admin user**: Always created with known credentials
- **Regular users**: Realistic usernames and email addresses
- **Passwords**: Properly hashed using FastAPI Users
- **Attributes**: Random mix of verified/unverified, active users

### Cards
- **Names**: Inspired by trading card games
- **Text**: Realistic card abilities and descriptions
- **Types**: Creatures, spells, artifacts, enchantments, lands
- **Variety**: Balanced mix across different themes

### Decks
- **Themes**: Coherent deck archetypes (aggro, control, combo)
- **Ownership**: Randomly assigned to users
- **Validation**: Mix of valid and invalid decks
- **Size**: Realistic deck sizes (15-60 cards)

### Deck-Card Relationships
- **Quantities**: Realistic card quantities (1-4 copies)
- **Distribution**: Balanced across card types
- **Uniqueness**: No duplicate card entries per deck

## Script Dependencies

All scripts require:
- Tortoise ORM initialized
- Database connection configured
- FastAPI Users for password hashing
- All model classes imported

The scripts automatically handle:
- Database initialization
- Connection management
- Error handling
- Progress reporting

## Tips

1. **Start Small**: Use `quick_populate.py` for initial development
2. **Build Up**: Use `generate_data.py` for more comprehensive testing
3. **Specialize**: Use `generate_mtg_cards.py` for card-heavy testing
4. **Monitor**: Use `db_utils.py --stats` to check database state
5. **Backup**: Use `db_utils.py --export` before major changes

## Error Handling

All scripts include proper error handling and will:
- Report progress during execution
- Show clear error messages
- Clean up database connections
- Provide helpful success summaries

If a script fails, check:
- Database connection settings
- Model imports
- Database permissions
- Available disk space (for exports)
